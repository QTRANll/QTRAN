# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 11:27
# @Author  : zql
# @File    : Info_Crawler.py
# @Intro   : 获取MySQL的关于sql statements的所有信息

import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag
import re
from src.FeatureKnowledgeBase_Code.crawler_options import set_options


def is_illustration(tag_name, tag_class, tag_text):
    # 判断Tag是否为illustration：是则返回True，否则返回False
    if tag_name == 'div' and 'titlepage' in tag_class:
        #  跳过标题
        return False
    elif tag_name == 'div' and 'copytoclipboard-wrapper' in tag_class and ";" not in tag_text:
        #  跳过feature
        return False
    elif tag_text == "":
        #  跳过空文本
        return False
    elif tag_name == 'div' and 'toc' in tag_class:
        #  跳过顶部的子statement链接列表
        return False
    return True


#  获取illustration:遍历处理Document Body的内容并获取overall illustration和detailed illustration
def document_body_processor(soup_docs_body):
    illustrations = []  # 存储处理的每一条illustration
    subtitle_indexes = []  # 存储每个SubTitle在illustrations数组中的下标
    for item in soup_docs_body.children:
        #  跳过非Tag
        if isinstance(item, Tag) == 0:
            continue

        item_name = item.name
        item_class = item.get("class")
        item_text = item.text
        #  跳过非illustration的Tag
        if not is_illustration(item_name, item_class, item_text):
            continue

        #  如果是SubTitle，则记录下标
        if item_name == 'h4':
            subtitle_indexes.append(len(illustrations))
        illustrations.append(item_text)

    # 遍历处理illustration形成最终结果
    detailed_illustration = []

    if len(subtitle_indexes) == 0:
        # 没有SubTitle
        overall_illustration = illustrations
    else:
        # 有SubTitle
        overall_illustration = illustrations[0:subtitle_indexes[0]]
        for i in range(len(subtitle_indexes)):
            start_index = subtitle_indexes[i]
            if i == len(subtitle_indexes)-1:
                end_index = len(illustrations)
            else:
                end_index = subtitle_indexes[i+1]

            detail = {"Sub-title": illustrations[start_index], "Illustration": illustrations[start_index + 1:end_index]}

            detailed_illustration.append(detail)

    return overall_illustration, detailed_illustration


# 爬取无子statement的SQL statement的信息并存储
def sql_statements_crawler(title, html):
    result = {}

    dir_filename = prefix + "SQL_Statements/SQL_Statements_Results/" + title + ".json"
    if os.path.exists(dir_filename):
        print("文件 " + dir_filename + " 已存在！")
        return

    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 获取html
    result["HTML"] = html
    # 获取SQL Statement Title
    # Result["Title"] = soup.find("h3",class_="title").text
    result["Title"] = title

    # 获取feature和example：读取所有language-sql代码块儿文本（不包括终端的代码块language-terminal）
    code_blocks = soup.findAll("code", class_="language-sql")
    # Feature：不包含分号的；Example：包含分号的
    result["Feature"] = []
    result["Examples"] = []
    for block in code_blocks:
        if ";" in block.text:
            result["Examples"].append(block.text)
        else:
            result["Feature"].append(block.text)

    # 获取illustration
    soup_docs_body = soup.find("div", id="docs-body").find("div", class_="section")
    overall_illustration, detailed_illustration = document_body_processor(soup_docs_body)
    result["Overall Illustration"] = overall_illustration
    result["Detailed Illustration"] = detailed_illustration

    with open(dir_filename, 'a', encoding='utf-8') as f:
        json.dump(result, f, indent=4)


def crawler_results(htmls_filename):
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
        for key, value in html_contents.items():
            if key.count('.') == 1:
                continue
            print(key)
            print(value)
            sql_statements_crawler(key, value)
            print('----------------------')


# 对爬取的sql statements的results进行分类
def information_classify(results_dicname, results_cat_dicname):
    category = [
        "",
        "Data Definition Statements",
        "Data Manipulation Statements",
        "Transactional and Locking Statements",
        "Replication Statements",
        "Prepared Statements",
        "Compound Statement Syntax",
        "Database Administration Statements",
        "Utility Statements"
    ]
    filenames_dic = os.listdir(results_dicname)
    for index in range(1, len(category)):
        if os.path.exists(results_cat_dicname+'/' + category[index] + ".json"):
            continue
        type_name = "15." + str(index)  # 1-8，没有两位数
        results = {}
        for filename in filenames_dic:
            if type_name in filename:
                # 读取文件内的内容
                with open(results_dicname + '/' + filename, "r", encoding="utf-8") as rf:
                    content = json.load(rf)
                    content["Category"] = []
                    content["Category"].append(category[index])
                # 将Category补充写入
                with open(results_dicname + '/' + filename, "w", encoding="utf-8") as wf:
                    json.dump(content, wf, indent=4)
                feature = re.sub(rf'{filename.split(" ")[0] + " "}+', '', filename)
                feature = feature.split('.')[0]
                results[feature] = content
        with open(results_cat_dicname + '/' + category[index] + ".json", 'a',
                  encoding='utf-8') as f:
            json.dump(results, f, indent=4)


prefix = "../../../Feature Knowledge Base/MySQL/"
Htmls_Filename = prefix + "SQL_Statements/SQL_Statements_HTMLs.json"
crawler_results(Htmls_Filename)  # 爬取statement的每个页面的信息并存储

Results_Dicname = prefix + "SQL_Statements/SQL_Statements_Results"
Results_Cat_Dicname = prefix + "SQL_Statements/SQL_Statements_Results_Category"
information_classify(Results_Dicname, Results_Cat_Dicname)  # 对爬取到的statement信息进行分类
