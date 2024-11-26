# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 11:27
# @Author  : zql
# @File    : Info_Crawler.py
# @Intro   : 获取MySQL的关于sql statements的所有信息

import json
import os
# from exceptiongroup import catch
# from prompt_toolkit.layout.processors import PasswordProcessor
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag
import re
from src.Tools.Crawler.crawler_options import set_options
from urllib.parse import urljoin

def is_illustration(tag_name, tag_class, tag_text):
    if tag_text == "":
        #  跳过空文本
        return False
    return True


def operators_crawler_results(origin_category,html,results_dicname, mysql_results_dic):
    # 获取所有operators的信息：从已爬取好的mysql8.4中检索，以reference html作为key进行检索（注：TiDB的operators链接中，需要将8.0修改为8.4）
    results_files_mysql = os.listdir(mysql_results_dic)
    # 从mysql的对应类别信息中查找到所需信息：以html_new作为查找的key
    for file in results_files_mysql:
        with open(os.path.join(mysql_results_dic, file), "r", encoding="utf-8") as r:
            value = json.load(r)
        if html == value["Reference HTML"]:
            # 修改value的内容
            category_temp = value["Category"]
            if "Built-In Functions and Operators" in category_temp and len(category_temp) > 1:
                category_temp.remove("Built-In Functions and Operators")
            value_new = {
                "HTML": html,
                "Title": value["Name"],
                "Feature": value["Feature"],
                "Description": value["Description"],
                "Examples": value["Examples"],
                "Category": category_temp
            }
            file_cnt = len(os.listdir(results_dicname))
            result_filename = os.path.join(results_dicname, str(file_cnt) + ".json")
            with open(result_filename, "w", encoding="utf-8") as w:
                json.dump(value_new, w, indent=4, ensure_ascii=False)


def functions_crawler_results_subtitle(category, html, results_dicname, function_names):
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 获取functions相关文档信息的div块
    soup_div = soup.find("div", class_="markdown-body MuiBox-root css-0")
    if not soup_div:
        return

    # 获取statements“示例”模块中的所有examples
    subtitle_indexes = []  # 所有functions names的index
    subtitle_hrefs = []  # 所有functions names的对应链接
    pre_indexes = []  # 所有pre类型代码块的下标
    doc_items = []  # 所有文档内容的txt

    for item in soup_div.children:
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
        if (item_name == 'h2' or item_name == 'h3' or item_name == 'h4') and item_text in function_names:
            subtitle_indexes.append(len(doc_items))
            subtitle_hrefs.append(urljoin(html, item.find("a").get("href")))
        if item_name == 'pre':
            pre_indexes.append(len(doc_items))
        doc_items.append(item_text)

    # 依次处理所有functions的信息
    for subtitle_index in subtitle_indexes:
        result_temp = {}
        docs_start_index = subtitle_index
        if subtitle_indexes.index(subtitle_index) == len(subtitle_indexes)-1:
            docs_end_index = len(doc_items)
        else:
            docs_end_index = subtitle_indexes[subtitle_indexes.index(subtitle_index) + 1]
        # result_temp["HTML"] = [subtitle_hrefs[subtitle_indexes.index(subtitle_index)]]
        result_temp["HTML"] = [html]
        result_temp["Title"] = [doc_items[subtitle_index]]
        result_temp["Feature"] = [doc_items[subtitle_index]]  # 默认值为标题
        result_temp["Description"] = []
        result_temp["Examples"] = []
        result_temp["Category"] = [category]
        description_end_flag = False
        for doc_index in range(docs_start_index, docs_end_index):
            if "示例" in doc_items[doc_index]:
                description_end_flag = True
            if not description_end_flag:
                result_temp["Description"].append(doc_items[doc_index])
            if doc_index in pre_indexes and ";" in doc_items[doc_index]:
                result_temp["Examples"].append(doc_items[doc_index])
        file_cnt = len(os.listdir(results_dicname))
        result_filename = os.path.join(results_dicname, str(file_cnt) + ".json")
        with open(result_filename, "w", encoding="utf-8") as w:
            json.dump(result_temp, w, indent=4, ensure_ascii=False)

def is_valid_sql_function_name(name):
    """
    判断字符串是否是有效的 SQL 函数名
    SQL 函数命名规则：
    - 只能包含字母、数字和下划线
    - 不能以数字开头
    - 不能是空字符串
    """
    # 使用正则表达式匹配：字母或下划线开头，后面可以是字母、数字或下划线
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name.replace("(","").replace(")","")))

def functions_crawler_results(origin_category,html, results_dic, mysql_results_dic):
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    mysql_functions = {}  # 存储table中列出的functions names和对应的htmls
    tidb_functions = []  # 存储导航栏中列出的functions names

    # 提取页面内导航栏的所有函数名称
    soup_muibox = soup.find("nav", class_="MuiBox-root css-0")
    soup_a_items = soup_muibox.find_all("a")
    for a_item in soup_a_items:
        a_name = a_item.text
        a_html = urljoin(html, a_item.get("href"))
        if is_valid_sql_function_name(a_name.replace("(", "").replace(")", "")):
            tidb_functions.append(a_name)

    # 读取页面内的table内容，将有mysql相关链接的names记录下来
    soup_tables = soup.find_all("table")
    # 分别处理所有的table
    for index in range(len(soup_tables)):
        soup_table = soup_tables[index]
        soup_thead = soup_table.find("thead")
        # 判断table是否为functions相关的：判断thead中是否包含字符串"函数名"，如果不包含则跳过该table
        if "函数名" not in soup_thead.text:
            continue
        soup_body = soup_table.find("tbody") if soup_table else None
        soup_trs = soup_body.find_all("tr")
        # 遍历table内所有tr
        for soup_tr in soup_trs:
            soup_td_first = soup_tr.find("td")
            name_temp = soup_td_first.text
            html_temp = soup_td_first.find("a").get("href")
            if "mysql.com" in html_temp and name_temp not in tidb_functions:
                mysql_functions[name_temp] = html_temp

    # 情况1：处理mysql_functions类型的
    for func_name, func_html in mysql_functions.items():
        operators_crawler_results(origin_category, func_html, results_dic, mysql_results_dic)
    # 情况2：处理tidb_functions类别的
    functions_crawler_results_subtitle(origin_category, html, results_dic, tidb_functions)

def data_types_crawler_results(origin_category,html, results_dic):
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    tidb_functions = []  # 存储导航栏中列出的functions names

    # 提取页面内导航栏的所有函数名称
    soup_muibox = soup.find("nav", class_="MuiBox-root css-0")
    soup_a_items = soup_muibox.find_all("a")
    for a_item in soup_a_items:
        a_name = a_item.text
        a_html = urljoin(html, a_item.get("href"))
        if is_valid_sql_function_name(a_name.replace("(", "").replace(")", "").replace("类型", "").strip()):
            tidb_functions.append(a_name)
    functions_crawler_results_subtitle(origin_category, html, results_dic, tidb_functions)


def crawler_results(feature_type, htmls_filename, dic_filename):
    if len(os.listdir(dic_filename)):
        print(dic_filename + ":Crawler finished")
        return
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
    for category_key, value in html_contents.items():
        for statement_key, statement_value in value.items():
            print(statement_key + ":" + str(statement_value))
            if feature_type == "operator":
                operators_crawler_results(statement_key,statement_value, dic_filename, dic_filename.replace("tidb", "mysql"))
            elif feature_type == "function":
                functions_crawler_results(statement_key,statement_value, dic_filename, dic_filename.replace("tidb", "mysql"))
            elif feature_type == "datatype":
                data_types_crawler_results(statement_key,statement_value, dic_filename)
            print('----------------------')
