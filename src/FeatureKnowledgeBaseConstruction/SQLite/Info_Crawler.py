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
from src.Tools.Crawler.crawler_options import set_options


def is_illustration(tag_name, tag_class, tag_text):
    if tag_text == "":
        #  跳过空文本
        return False
    return True

def functions_crawler_results_json(category, html, results_dicname):
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_div = soup.find("div", class_="fancy")

    subtitle_indexes = []  # 所有functions names的index
    code_indexes = []  # 所有pre类型代码块的下标
    doc_items = []  # 所有文档内容的txt
    functions_flag = False
    for item in soup_div.children:
        #  跳过非Tag
        if isinstance(item, Tag) == 0:
            continue
        item_name = item.name
        item_class = item.get("class")  # 注意：item_class是列表形式的
        item_text = item.text
        if "Function Details" in item_text and item_name == "h1":
            functions_flag = True
        if not functions_flag: continue
        #  跳过非有效文本内容的Tag
        if not is_illustration(item_name, item_class, item_text):continue

        #  如果是SubTitle，则记录下标
        if item_name == 'h2':
            subtitle_indexes.append(len(doc_items))
            doc_items.append(item_text)
        elif item_name == "ul":
            for li in item.find_all("li"):
                code_indexes.append(len(doc_items))
                doc_items.append(li.text)
        else:
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
        result_temp["Description"] = doc_items[docs_start_index:docs_end_index]
        result_temp["Examples"] = []
        result_temp["Category"] = [category]
        for doc_index in range(docs_start_index, docs_end_index):
            if doc_index in code_indexes:
                result_temp["Examples"].append(doc_items[doc_index])
        file_cnt = len(os.listdir(results_dicname))
        result_filename = os.path.join(results_dicname, str(file_cnt) + ".json")
        with open(result_filename, "w", encoding="utf-8") as w:
            json.dump(result_temp, w, indent=4, ensure_ascii=False)

def functions_crawler_results(origin_category,html, results_dic, mysql_results_dic):
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_dl = soup.find_all("dl")
    for item in soup_dl:
        soup_dts = item.find_all("dt")
        soup_dds = item.find_all("dd")
        for index in range(len(soup_dts)):
            function_res = {
                "HTML": [html],
                "Title": [soup_dts[index].text],
                "Feature": [soup_dts[index].text],
                "Description": [soup_dds[index].text],
                "Examples": [],
                "Category": [origin_category]
            }
            file_cnt = len(os.listdir(results_dic))
            result_filename = os.path.join(results_dic, str(file_cnt) + ".json")
            with open(result_filename, "w", encoding="utf-8") as w:
                json.dump(function_res, w, indent=4, ensure_ascii=False)
    if "JSON function" == origin_category:
        functions_crawler_results_json(origin_category, html, results_dic)


def crawler_results(feature_type, htmls_filename, dic_filename):
    if len(os.listdir(dic_filename)):
        print(dic_filename + ":Crawler finished")
        return
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
    for category_key, value in html_contents.items():
        for statement_key, statement_value in value.items():
            print(statement_key + ":" + str(statement_value))
            if feature_type == "function":
                functions_crawler_results(statement_key,statement_value, dic_filename, dic_filename.replace("tidb", "mysql"))
            print('----------------------')
