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
from bs4 import BeautifulSoup, Tag
from src.Tools.Crawler.crawler_options import set_options

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
    for tr in trs:
        td_contents = []
        # 判断第一个值是否为别名相关
        if tr.find("td").text.strip().lower() in ["alias(es)", "aliases", "alias"]:
            td_contents.append(tr.find("td").text.strip())
            code_temp = ""
            for td in tr.find_all("td"):
                if td.text.strip() in td_contents or "-" == td.text.strip():
                    continue
                codes = td.find_all("code")
                for code in codes:
                    code_temp += code.text.strip() + ";"
            td_contents.append(code_temp[:-1])
        else:
            for td in tr.find_all("td"):
                td_contents.append(td.text.strip())
        soup_tbody_contents.append(td_contents)
    return soup_tbody_contents


def function_crawler(origin_category, title, html, dic_filename):
    result = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_div = soup.find("div", id="main_content_wrap")
    soup_tables = soup_div.find_all("table")  # 获取所有的table

    functions_dic = {}

    # 遍历处理所有的table：获取table的列名
    for table in soup_tables:
        # 列名：只包含下面几个，Function（Name），Description，Example
        column_names = get_table_column_names(table.find("thead"))
        # 判断列名内是否含有：Function或Name，如果有则是function相关的列表
        if ("Function" in column_names or "Name" in column_names) and "Description" in column_names:
            # 处理关于functions的列表：先获取table的所有数据条
            table_contents = get_table_column_contents(table.find("tbody"))
            # 处理读取到的所有table数据条
            for content in table_contents:
                feature_temp = [content[column_names.index("Function")]] if "Function" in column_names else [content[column_names.index("Name")]]
                description_temp = [content[column_names.index("Description")]] if "Description" in column_names else []
                example_temp = [content[column_names.index("Example")]] if "Example" in column_names else []

                function_res = {
                    "HTML": [html],
                    "Title": feature_temp,
                    "Feature": feature_temp,
                    "Description": description_temp,
                    "Examples": example_temp,
                    "Category": [origin_category]
                }

                functions_dic[feature_temp[0]] = function_res

    # 二次遍历所有的table，获取其中function的详细信息并添加存储到dic中
    for item in soup_div.children:
        #  跳过非Tag
        if isinstance(item, Tag) == 0:
            continue
        # 获取每个文本块的类型信息
        item_name = item.name
        item_class = item.get("class")  # 注意：item_class是列表形式的
        item_text = item.text

        # 寻找<div class="nostroke_table"></div>:这元素的前一个兄弟节点是function的title，后一个节点是function的详细描述
        if item_name == "div" and "nostroke_table" in item_class:
            # 获取该元素的function name,在function_dic中找到对应的key（如果已存在）并进行信息补充，如果不存在就作为新增字典键值对
            function_name = item.find_previous_sibling().text.strip()
            # 获取该元素的详细信息
            # Description，Example，Alias(es)，Aliases，Alias，Result，Formula等其他不常见的则全部归为description即可，其中别名可能有多个
            contents = get_table_column_contents(item.find_next_sibling().find("tbody"))
            # 初始化结果值
            function_result_temp = None
            if function_name in functions_dic:
                function_result_temp = functions_dic[function_name]
            else:
                function_result_temp = {
                    "HTML": [html],
                    "Title": [function_name],
                    "Feature": [function_name],
                    "Description": [],
                    "Examples": [],
                    "Category": [origin_category]
                }
            # 按照行处理详细信息
            description_add = []
            example_add = []
            alias_add = []
            for content in contents:
                if content[0].lower() in ["example", "examples"]:
                    example_add.append(content[-1])
                elif content[0].lower() in ["alias(es)", "aliases", "alias"]:
                    # 特殊处理有别名的情况：为这些别名的情况作特殊处理
                    for alias in content[-1].split(";"):
                        if "-" not in alias and len(alias):
                            alias_add.append(alias)
                elif content[0].lower() in ["result"]:
                    continue
                else:
                    description_add.append(content[-1])

            # 将详细信息添加到已有function信息中
            for des in description_add:
                if des not in function_result_temp["Description"]:
                    function_result_temp["Description"].append(des)

            for ex in example_add:
                if ex not in function_result_temp["Examples"]:
                    function_result_temp["Examples"].append(ex)

            # 处理涉及到的alias:为所有的别名添加新的（或者在已有的上进行补充）信息
            for alias in alias_add:
                if alias in functions_dic:
                    continue
                else:
                    functions_dic[alias] = function_result_temp
                    functions_dic[alias]["Description"] = functions_dic[alias]["Feature"] + functions_dic[alias]["Description"]
                    functions_dic[alias]["Title"] = [alias]
                    functions_dic[alias]["Feature"] = [alias]
                    print(alias)
            functions_dic[function_name] = function_result_temp

    # 存储所有的function的内容
    for key, value in functions_dic.items():
        file_cnt = len(os.listdir(dic_filename))
        filename = str(file_cnt) + ".json"
        if os.path.exists(os.path.join(dic_filename, filename)):
            print(filename+":已经存在")
        with open(os.path.join(dic_filename, filename), "w", encoding="utf-8") as w:
            json.dump(value, w, indent=4)

def op_crawler(origin_category, title, html, dic_filename):
    result = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_div = soup.find("div", id="main_content_wrap")
    soup_tables = soup_div.find_all("table")  # 获取所有的table

    functions_dic = {}
    # 遍历处理所有的table：获取table的列名
    for table in soup_tables:
        # 列名：只包含下面几个，Operator, Description, Example, Result
        column_names = get_table_column_names(table.find("thead"))
        # 判断列名内是否含有：Operator，如果有则是operator相关的列表
        if "Operator" in column_names:
            # 处理关于functions的列表：先获取table的所有数据条
            table_contents = get_table_column_contents(table.find("tbody"))
            # 处理读取到的所有table数据条
            for content in table_contents:
                feature_temp = [content[column_names.index("Operator")]] if "Operator" in column_names else []
                description_temp = [content[column_names.index("Description")]] if "Description" in column_names else []
                example_temp = [content[column_names.index("Example")]] if "Example" in column_names else []

                function_res = {
                    "HTML": [html],
                    "Title": feature_temp,
                    "Feature": feature_temp,
                    "Description": description_temp,
                    "Examples": example_temp,
                    "Category": [origin_category]
                }
                functions_dic[function_res["Description"][0]] = function_res

    # 存储所有的operator的内容
    for key, value in functions_dic.items():
        file_cnt = len(os.listdir(dic_filename))
        filename = str(file_cnt) + ".json"
        if os.path.exists(os.path.join(dic_filename, filename)):
            print(filename+":已经存在")
        with open(os.path.join(dic_filename, filename), "w", encoding="utf-8") as w:
            json.dump(value, w, indent=4)

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
    soup_div = soup.find("div", id="main_content_wrap")
    for item in soup_div:
        if len(item.text.strip()):
            detailed["Description"].append(item.text)
    soup_pres = soup.find_all("pre", class_="highlight")
    for item in soup_pres:
        soup_codes = item.find_all("code")
        for code in soup_codes:
            if len(code.text.strip()):
                detailed["Examples"].append(code.text)
    file_cnt = len(os.listdir(dic_filename))
    with open(os.path.join(dic_filename, str(file_cnt) + ".json"), "w", encoding="utf-8") as w:
        json.dump(detailed, w, indent=4)

def crawler_results(feature_type, htmls_filename, dic_filename):
    if len(os.listdir(dic_filename)):
        print(dic_filename + ":Crawler finished")
        return
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
        for category_key, value in html_contents.items():
            for statement_key, statement_value in value.items():
                print(statement_key+":"+str(statement_value))
                if feature_type == "function":
                    function_crawler(statement_key, statement_key, statement_value, dic_filename)
                elif feature_type == "operator":
                    op_crawler(statement_key.replace("function", "operator"), statement_key, statement_value, dic_filename)
                elif feature_type == "datatype":
                    data_types_crawler(category_key, statement_key, statement_value, dic_filename)
                print('----------------------')


