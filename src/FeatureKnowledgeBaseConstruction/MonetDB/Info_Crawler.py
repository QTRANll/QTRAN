# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/28 10:16
# @Author  : shaocanfan
# @File    : Info_Crawler.py
# @Intro   :


import json
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from src.Tools.Crawler.crawler_options import set_options
from src.Tools.Crawler.crawler_options import sanitize_title
"""
column_names_temp = []
column_htmls_temp = []
"""

def get_table_column_names(soup_thead):
    soup_thead_names = []
    if not soup_thead:
        return soup_thead_names
    ths = soup_thead.find_all("th")
    for th in ths:
        soup_thead_names.append(th.text.strip())
    return soup_thead_names

def get_table_column_contents(soup_tbody):
    soup_tbody_contents = []
    if not soup_tbody:
        return soup_tbody_contents
    trs = soup_tbody.find_all("tr")
    # 处理多列
    for tr in trs:
        info_contents = []  # 内部存储多个[]格式的信息，因为feature，description和example都可能不止一个
        # 获取tr内的所有td，处理
        for td in tr.find_all("td"):
            info_contents.append([td.text.strip()])
        soup_tbody_contents.append(info_contents)
    return soup_tbody_contents


def function_crawler(origin_category, title, html, func_dic_filename, op_dic_dicname):
    result = {}
    table_include = [
        "Function",
        "Operator",
        "Statistic Function"
    ]
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_tables = soup.find_all("table", class_="table-bordered")  # 获取所有的table

    functions_dic = {}
    operators_dic = {}

    # 遍历处理所有的table：获取table的列名
    for table in soup_tables:
        # 列名：只包含下面几个，Function（Name），Description，Example
        column_names = get_table_column_names(table.find("thead"))
        if column_names[0] not in table_include:
            continue
        """
        if column_names not in column_names_temp:
            column_names_temp.append(column_names)
            column_htmls_temp.append(html)
        """

        # 第一列在下列范围，视为functions和operators相关（也是feature列）表格：Function，Operator，Statistic Function
        # Description列：Return type（添加returen type的说明），Argument types（添加arguments type的说明），Description
        # Examples列：Example

        feature_column_indexes = []
        description_column_indexes = []
        examples_column_indexes = []
        # 遍历columns names，记录各个分类的indexes
        for name_index in range(len(column_names)):
            if column_names[name_index] in ["Function", "Operator", "Statistic Function"]:
                feature_column_indexes.append(name_index)
            elif column_names[name_index] in ["Return type", "Argument types", "Description"]:
                description_column_indexes.append(name_index)
            elif column_names[name_index] in ["Example"]:
                examples_column_indexes.append(name_index)

        # 处理列表：先获取table的所有数据条
        table_contents = get_table_column_contents(table.find("tbody"))
        # 处理读取到的所有table数据条
        for content in table_contents:
            feature_temp = []
            description_temp = []
            examples_temp = []
            for index in feature_column_indexes:
                feature_temp += content[index]
            for index in description_column_indexes:
                if column_names[index] == "Return type":
                    description_temp.append("Return type: ")
                elif column_names[index] == "Argument types":
                    description_temp.append("RArgument types: ")
                description_temp += content[index]
            for index in examples_column_indexes:
                examples_temp += content[index]
            function_res = {
                "HTML": [html],
                "Title": feature_temp,
                "Feature": feature_temp,
                "Description": description_temp,
                "Examples": examples_temp,
                "Category": [origin_category]
            }

            # 判断属于function还是operator
            # 只包含Operator：Operator
            # 只包含Function：Function，Function signature
            print(function_res)
            key_temp = feature_temp[0]
            new_category = origin_category.split("function")[0]
            if "Operator" in column_names[0]:
                # 修改category
                function_res["Category"] = [new_category+"operator"]
                operators_dic[key_temp] = function_res
            elif "Function" in column_names[0]:
                function_res["Category"] = [new_category + "function"]
                functions_dic[key_temp] = function_res

    # 存储所有的function的内容
    for key, value in functions_dic.items():
        file_cnt = len(os.listdir(func_dic_filename))
        filename = str(file_cnt) + ".json"
        if os.path.exists(os.path.join(func_dic_filename, filename)):
            print(filename+":已经存在")
        with open(os.path.join(func_dic_filename, filename), "w", encoding="utf-8") as w:
            json.dump(value, w, indent=4, ensure_ascii=False)

    # 存储所有的operators的内容
    for key, value in operators_dic.items():
        file_cnt = len(os.listdir(op_dic_dicname))
        filename = str(file_cnt) + ".json"
        if os.path.exists(os.path.join(op_dic_dicname, filename)):
            print(filename+":已经存在")
        with open(os.path.join(op_dic_dicname, filename), "w", encoding="utf-8") as w:
            json.dump(value, w, indent=4, ensure_ascii=False)

def data_types_crawler(category_key, statement_key, statement_value, dic_filename):
    detailed = {
        "HTML": [statement_value],
        "Title": [statement_key],
        "Feature": [statement_key],
        "Description": [],
        "Examples": [],
        "Category": [statement_key]
    }
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(statement_value)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_div = soup.find("div", id="body-inner")

    # 处理包含tables的情况
    soup_tables = soup_div.find_all("table", class_="table-bordered")  # 获取所有的table
    table_include = ["Name", "SQL data type", "Column name"]
    for table in soup_tables:
        # 列名：只包含下面几个，Function（Name），Description，Example
        column_names = get_table_column_names(table.find("thead"))
        if column_names[0] not in table_include:
            continue
        feature_column_indexes = [0]
        description_column_indexes = range(1,len(column_names))
        # 处理列表：先获取table的所有数据条
        table_contents = get_table_column_contents(table.find("tbody"))
        # 处理读取到的所有table数据条
        for content in table_contents:
            feature_temp = []
            description_temp = []
            for index in feature_column_indexes:
                feature_temp += content[index]
            for index in description_column_indexes:
                description_temp += content[index]
            res = {
                "HTML": [statement_value],
                "Title": feature_temp,
                "Feature": feature_temp,
                "Description": description_temp,
                "Examples": [],
                "Category": [statement_key]
            }
            file_cnt = len(os.listdir(dic_filename))
            with open(os.path.join(dic_filename, str(file_cnt) + ".json"), "w", encoding="utf-8") as w:
                json.dump(res, w, indent=4)

    if len(soup_tables): return
    for item in soup_div:
        if len(item.text.strip()):
            detailed["Description"].append(item.text)
    soup_codes = soup_div.find_all("code", class_="language-pre")
    for item in soup_codes:
        if len(item.text.strip()):
                detailed["Examples"].append(item.text)
    file_cnt = len(os.listdir(dic_filename))
    with open(os.path.join(dic_filename, str(file_cnt) + ".json"), "w", encoding="utf-8") as w:
        json.dump(detailed, w, indent=4)


def crawler_results(feature_type, func_htmls_filename, func_dic_filename, op_dir_dicname):
    if len(os.listdir(func_dic_filename)):
        print(func_dic_filename+ ":Crawler finished")
        return
    with open(func_htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
        for category_key, value in html_contents.items():
            for statement_key, statement_value in value.items():
                print(statement_key+":"+str(statement_value))
                if feature_type in ["function", "operator"]:
                    origin_category = sanitize_title(statement_key.strip())
                    print(origin_category)
                    function_crawler(origin_category, statement_key, statement_value, func_dic_filename, op_dir_dicname)
                elif feature_type == "datatype":
                    data_types_crawler(category_key, statement_key, statement_value, func_dic_filename)
                print('----------------------')


