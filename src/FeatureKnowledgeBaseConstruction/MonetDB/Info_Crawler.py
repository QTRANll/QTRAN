# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/28 10:16
# @Author  : shaocanfan
# @File    : Info_Crawler.py
# @Intro   :


import json
import os
import glob
# from exceptiongroup import catch
# from prompt_toolkit.layout.processors import PasswordProcessor
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from src.Tools.Crawler.crawler_options import set_options
from src.Tools.Crawler.crawler_options import sanitize_title


column_names_temp = []
column_htmls_temp = []


def is_illustration(tag_name, tag_class, tag_text):
    if tag_text == "":
        #  跳过空文本
        return False
    return True
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

        if column_names not in column_names_temp:
            column_names_temp.append(column_names)
            column_htmls_temp.append(html)

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
            new_category = origin_category.split("Functions")[0]
            if "Operator" in column_names[0]:
                # 修改category
                function_res["Category"] = [new_category+"Operators"]
                operators_dic[key_temp] = function_res
            elif "Function" in column_names[0]:
                function_res["Category"] = [new_category + "Functions"]
                functions_dic[key_temp] = function_res

    # 存储所有的function的内容
    for key, value in functions_dic.items():
        file_cnt = len(os.listdir(func_dic_filename))
        filename = str(file_cnt) + "_" + sanitize_title(key) + ".json"
        if os.path.exists(os.path.join(func_dic_filename, filename)):
            print(filename+":已经存在")
        with open(os.path.join(func_dic_filename, filename), "w", encoding="utf-8") as w:
            json.dump(value, w, indent=4, ensure_ascii=False)

    # 存储所有的operators的内容
    for key, value in operators_dic.items():
        file_cnt = len(os.listdir(op_dic_dicname))
        filename = str(file_cnt) + "_" + sanitize_title(key) + ".json"
        if os.path.exists(os.path.join(op_dic_dicname, filename)):
            print(filename+":已经存在")
        with open(os.path.join(op_dic_dicname, filename), "w", encoding="utf-8") as w:
            json.dump(value, w, indent=4, ensure_ascii=False)


def crawler_results(feature_type, func_htmls_filename, func_dic_filename, op_htmls_filename, op_dir_dicname):
    with open(func_htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
        for category_key, value in html_contents.items():
            for statement_key, statement_value in value.items():
                print(statement_key+":"+str(statement_value))
                if feature_type in ["function", "op"]:
                    origin_category = sanitize_title(statement_key.strip())
                    print(origin_category)
                    function_crawler(origin_category, statement_key, statement_value, func_dic_filename, op_dir_dicname)
                print('----------------------')


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"文件 '{file_path}' 已成功删除。")
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在。")
    except PermissionError:
        print(f"没有权限删除文件 '{file_path}'。")
    except Exception as e:
        print(f"删除文件时发生错误: {e}")

def category_classifier(results_dicname, results_category_dicname):
    # 对爬取的所有结果以category进行分类并存储到SQL_Statements_Results_Category中
    json_files = glob.glob(os.path.join(results_dicname, '*.json'))
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as r:
            data = json.load(r)

        # 将结果存储到对应的jsonl文件中,可能属于多个类别
        for category in data["Category"]:
            with open(os.path.join(results_category_dicname, category + ".jsonl"), "a",encoding="utf-8") as w:
                json.dump(data, w)
                w.write('\n')


prefix = os.path.join("..", "..", "..", "Feature Knowledge Base", "MonetDB")

Function_Htmls_Filename = os.path.join(prefix, "Functions", "HTMLs.json")
Function_dir_dicname = os.path.join(prefix, "Functions", "Results")
Function_Results_Category_Dicname = os.path.join(prefix, "Functions", "Results_Category")

Ops_Htmls_Filename = os.path.join(prefix, "Operators", "HTMLs.json")
Op_dir_dicname = os.path.join(prefix, 'Operators', 'Results')
Op_Results_Category_Dicname = os.path.join(prefix, "Operators", "Results_Category")

# crawler_results("function", Function_Htmls_Filename, Function_dir_dicname, Ops_Htmls_Filename, Op_dir_dicname)
# category_classifier(Function_dir_dicname, Function_Results_Category_Dicname)  # 文件写入方式为add
# category_classifier(Op_dir_dicname, Op_Results_Category_Dicname)  # 文件写入方式为add


print(column_names_temp) # 统计所有的表格thead可能的情况
print(column_htmls_temp)
