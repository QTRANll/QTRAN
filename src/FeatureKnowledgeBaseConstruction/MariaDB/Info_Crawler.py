# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 11:27
# @Author  : zql
# @File    : Info_Crawler.py
# @Intro   : 获取MySQL的关于sql statements的所有信息

import json
import os
import glob
# from exceptiongroup import catch
# from prompt_toolkit.layout.processors import PasswordProcessor
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag
import re
from src.Tools.Crawler.crawler_options import set_options


def is_illustration(tag_name, tag_class, tag_text):
    if tag_text == "":
        #  跳过空文本
        return False
    elif tag_name == "div" and tag_class == ['table_of_contents', 'well', 'well-small' ]:
        # 跳过页面中的右侧导航栏
        return False
    return True


#  处理文档信息，获取feature,description和examples:遍历处理Document Body的内容并获取feature,description和examples
def document_body_processor(soup_body):
    feature = []
    description = []
    examples = []

    doc_items = []  # 存储处理文档中的每一条文本块
    subtitle_indexes = []  # 存储每个SubTitle在illustrations数组中的下标
    pre_indexes = []  # 存储每个代码块在illustrations数组中的下标
    if not soup_body: return

    for item in soup_body.children:
        #  跳过非Tag
        if isinstance(item, Tag) == 0:
            continue
        # 获取每个文本块的类型信息
        item_name = item.name
        item_class = item.get("class")  # 注意：item_class是列表形式的
        item_text = item.text
        #  跳过非有效文本内容的Tag
        if not is_illustration(item_name, item_class, item_text):continue

        #  如果是SubTitle，则记录下标
        if item_name == 'h2':
            subtitle_indexes.append(len(doc_items))

        # 如果是Pre，则记录下标
        if item_name == 'pre' and 'fixed' in item_class:
            pre_indexes.append(len(doc_items))
        doc_items.append(item_text)

    # 遍历处理doc_items的内容，以subtitle的下标为模块分界线:分别获取feature,description和examples的内容
    detailed_illustration = []
    for i in range(len(subtitle_indexes)):
        start_index = subtitle_indexes[i]
        if i == len(subtitle_indexes) - 1:
            # i为subtitle_indexes的最后一个下标
            end_index = len(doc_items)
        else:
            end_index = subtitle_indexes[i + 1]

        # 判断是否为feature,description和examples
        if doc_items[start_index] in ["Syntax", "syntax"]:
            feature = doc_items[start_index + 1:end_index]
        elif doc_items[start_index] in ["Description", "description"]:
            description = doc_items[start_index + 1:end_index]
        elif doc_items[start_index] in ["Examples", "examples", "Example", "example"]:
            # example只读取sql语句部分
            for example_index in range(start_index + 1, end_index):
                if example_index in pre_indexes:
                    examples.append(doc_items[example_index])
    return feature, description, examples

# 定义非法字符的替换规则
def sanitize_title(title):
    title = re.sub(r'<', 'less', title)
    title = re.sub(r'>', 'greater', title)
    title = re.sub(r':', 'colon', title)
    title = re.sub(r'\*', 'star', title)
    title = re.sub(r'[\/\\|?]', '_', title)  # 其他非法字符替换为下划线
    return title

# 爬取无子statement的SQL statement的信息并存储
def sql_statements_crawler(feature_type, origin_category, title, html, dic_filename):
    if title.startswith("Error") or len(html) == 0:
        return

    if os.path.exists(os.path.join(dic_filename, title + '.json')):
        print("文件 " + title + " 已存在！")
        return

    result = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 获取html
    result["HTML"] = [html]
    # 获取SQL Statement Title
    result["Title"] = soup.find("h1").text if soup.find("h1") else ""
    result["Title"] = [result["Title"]]
    # 使用函数处理标题
    dir_filename = os.path.join(dic_filename, str(len(os.listdir(dic_filename))) + '.json')

    if os.path.exists(dir_filename):
        print("文件 " + dir_filename + " 已存在！")
        return

    # 获取feature,description和examples,并根据页面上方导航目录确定category
    # 获取feature,description和examples：获取<div class="answer formatted">中所有信息，再对这些信息逐条处理，分割信息块
    soup_docs_body = soup.find("div", class_="node creole")
    soup_answer_formatted = soup_docs_body.find("div", class_="answer formatted") if soup_docs_body else []
    try:
        result["Feature"], result["Description"], result["Examples"] = document_body_processor(soup_answer_formatted)
    except Exception as e:
        print(e)
        return
    # 获取category：获取上方导航栏的目录内容,对于statement和fun_op有不同的处理方式
    soup_sub_header = soup.find("div", class_="breadcrumb", id="breadcrumbs")
    soup_a = soup_sub_header.find_all("a") if soup_sub_header else []
    soup_a_txt = [a.text for a in soup_a]
    if feature_type == "statements":
        # soup_a_text列表中'SQL Statements'后面的一个元素就是本条statement信息的category
        index = soup_a_txt.index('SQL Statements') if 'SQL Statements' in soup_a_txt else -1
    if feature_type == "operator":
        index = -1
    elif feature_type == "function":
        # soup_a_text列表中'Built-in function'后面的一个元素
        index = soup_a_txt.index('Built-in function') if 'Built-in function' in soup_a_txt else -1
        if "function" in soup_a_txt[index+2] or "functions" in soup_a_txt[index+2]:
            index += 1
    elif feature_type == "datatype":
        # soup_a_text列表中'Data Types'后面的一个元素
        index = soup_a_txt.index('Data Types') if 'Data Types' in soup_a_txt else -1
    else:
        index = -1
    if index != -1 and index + 1 < len(soup_a_txt):
        result["Category"] = [soup_a_txt[index + 1]]
    else:
        # 如果SQL Statements不在顶部目录导航栏中，则以原始的category填入
        result["Category"] = [origin_category]
        if "SEQUENCE function" in soup_a_txt:
            result["Category"] = ["SEQUENCE function"]
        elif "Spider function" in soup_a_txt:
            result["Category"] = ["Spider function"]
        elif "Vector function" in soup_a_txt:
            result["Category"] = ["Vector function"]
        elif "Geographic & Geometric Features" in soup_a_txt:
            result["Category"] = ["Geographic function"]
    try:
        if len(result["Feature"]) or len(result["Description"]) or len(result["Examples"]):
            with open(dir_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4)
    except Exception as e:
        print(e)
        return


def crawler_results(feature_type, htmls_filename, dic_filename):
    if len(os.listdir(dic_filename)):
        print(dic_filename+ ":Crawler finished")
        return
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
        for category_key, value in html_contents.items():
            for statement_key, statement_value in value.items():
                print(statement_key+":"+str(statement_value))
                sql_statements_crawler(feature_type, category_key, statement_key, statement_value, dic_filename)
                print('----------------------')


def preprocess_results(results_dicname):
    # 对爬取到的results进行预处理：处理description及feature均为空的feature；……
    json_files = glob.glob(os.path.join(results_dicname, '*.json'))
    synonym_filaname = os.path.join(os.path.dirname(results_dicname), "synonym_feature_filenames.jsonl")# 用于存储同义词feature
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as r:
            data = json.load(r)
        # 处理description及feature均为空的feature
        # 访问feature页面内容，判断网页内是否包含“A synonym for”。如果包含则获取同义feature的Title，在Functions_Results文件夹中检索该Title的json文件，若检索到则将信息copy为该feature的信息
        if len(data["Feature"]) == 0 and len(data["Description"]) == 0:
            print(data["Title"])
            timeout = 5  # 等待时间
            options = set_options()
            driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
            driver.get(data["HTML"])  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
            WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # 获取feature,description和examples：获取<div class="answer formatted">中所有信息，再对这些信息逐条处理，分割信息块
            soup_docs_body = soup.find("div", class_="node creole")
            soup_answer_formatted = soup_docs_body.find("div", class_="answer formatted") if soup_docs_body else []

            # 判断是否包含“A synonym for”
            if "synonym" in soup_answer_formatted.text.lower() or "alias" in soup_answer_formatted.text.lower():
                a = soup_answer_formatted.find("a")
                title_synonym = a.text.replace('(','').replace(')','') if a else ""  # 提取得到页面中关于当前feature的同义feature的title，不包含(),只包括feature名称
                for root, dirs, files in os.walk(results_dicname):
                    filenames_lower = [a.lower() for a in files]
                    print(title_synonym+".json")
                    if title_synonym.lower()+".json" in filenames_lower:
                        # 不区分大小写
                        print("文件在results中")
                        filename_selected_index = filenames_lower.index(title_synonym.lower()+".json")
                        filename_selected = files[filename_selected_index]
                        # 将当前feature的文件名写入同义词feature文件中进行记录
                        with open(synonym_filaname, "a", encoding="utf-8") as w:
                            json.dump({"filename":json_file.split('\\')[-1],"synonym filename":filename_selected}, w)
                            w.write('\n')
                        with open(os.path.join(results_dicname,filename_selected), "r", encoding="utf-8") as w:
                            synonym_data = json.load(w)
                        # 修改当下feature的"Feature"，"Description"，"Examples"以及category（从同义feature哪里copy过来），保留html，title
                        data["Feature"] = synonym_data["Feature"]
                        data["Description"] = synonym_data["Description"]
                        data["Examples"] = synonym_data["Examples"]
                        data["Category"] = synonym_data["Category"]

                        # 将copy并修改后的data信息存储到原文件中,暂时不存了
                        with open(json_file, "w", encoding="utf-8") as w:
                            json.dump(data, w, indent=4)
            print("---------------")


def category_classifier(results_dicname, results_category_dicname):
    # 对SQL_Statements_Results中爬取的所有结果以category进行分类并存储到SQL_Statements_Results_Category中
    json_files = glob.glob(os.path.join(results_dicname, '*.json'))
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as r:
            data = json.load(r)
        # 跳过无效的信息项
        if len(data["Feature"]) == 0:
            continue

        # 将结果存储到对应的jsonl文件中
        with open(os.path.join(results_category_dicname, data["Category"][0]+".jsonl"), "a", encoding="utf-8") as w:
            json.dump(data, w)
            w.write('\n')


