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
    processed_column_cnt = 0
    if not soup_thead:
        return soup_thead_names
    ths = soup_thead.find_all("th")
    ps = soup_thead.find_all("p")
    if len(ps):
        # 包含p，则只处理第一列th
        for p in ths[0].find_all("p"):
            if "example" in p.text.lower():
                p_txt = "Examples"
            else:
                p_txt = p.text.strip()
            soup_thead_names.append(p_txt)
        processed_column_cnt = 1
    else:
        # 不包含p，则处理所有列
        for th in ths:
            if "example" in th.text.lower():
                p_txt = "Examples"
            else:
                p_txt = th.text.strip()
            soup_thead_names.append(p_txt)
        processed_column_cnt = 2
    return soup_thead_names, processed_column_cnt


def get_table_column_contents(driver, soup_tbody, processes_columns_cnt):
    """
    * processes_columns_cnt:要处理的列数
    * 其中第一行，关于feature：以`<p class="func_signarure">`格式存储，个数不止一个
    * 第二行紧接着，关于desceription，以`<p>`格式存储，个数不止一个，class读取出来应该是none
    * 第三行紧接着（不是必有项），关于examples，以`<p>`格式存储，内部子节点包含`<code>`，个数不止一个
    :param soup_tbody:
    :return:
    """
    soup_tbody_contents = []
    if not soup_tbody:
        return soup_tbody_contents
    trs = soup_tbody.find_all("tr")
    if processes_columns_cnt == 1:
        for tr in trs:
            info_contents = []  # 内部存储多个[]格式的信息，因为feature，description和example都可能不止一个
            feature_temp = []
            description_temp = []
            example_temp = []
            # 获取tr内的的所有p标签
            p_elements = tr.find_all("p")
            for p in p_elements:
                # 为p分类：分类标准如下
                # p_class == "func_signature":feature
                # p_txt包含"→":examples
                # else:description
                p_class = p.get("class")
                p_txt = p.text.strip()
                if p_class:
                    if "func_signature" in p_class:
                        feature_temp.append(p_txt)
                else:
                    if "→" in p_txt:
                        example_temp.append(p_txt)
                    else:
                        description_temp.append(p_txt)
            info_contents = [feature_temp, description_temp, example_temp]
            soup_tbody_contents.append(info_contents)
    else:
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
    """
    table_include = [
        "Operator",
        "Function",
        "Function signature",
        "Function/Operator",
        "Operator/Method",
        "Predicate",
        "Predicate/Value"
    ]
    """
    table_include = [
        "Operator",
        "Function",
        "Function signature",
        "Function/Operator",
        "Operator/Method"
    ]
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # soup_div = soup.find("div", id="main_content_wrap")
    soup_tables = soup.find_all("table", class_="table")  # 获取所有的table

    functions_dic = {}
    operators_dic = {}

    # 遍历处理所有的table：获取table的列名
    for table in soup_tables:
        # 列名：只包含下面几个，Function（Name），Description，Example
        column_names, column_cnt = get_table_column_names(table.find("thead"))
        if column_names[0] not in table_include:
            continue
        if column_names not in column_names_temp:
            column_names_temp.append(column_names)
            column_htmls_temp.append(html)

        # 判断列名内是否含有：如果包含Description,说明非空，则是介绍feature的表格
        if len(column_names) and "Description" in column_names:
            # 处理列表：先获取table的所有数据条
            table_contents = get_table_column_contents(driver, table.find("tbody"), column_cnt)
            # 处理读取到的所有table数据条
            for content in table_contents:
                feature_temp = content[0] if type(content[0]) == list else [content[0]]
                description_temp = content[column_names.index("Description")] if "Description" in column_names else []
                if len(content) < 3:
                    example_temp = content[column_names.index("Examples")] if "Examples" in column_names else []
                else:
                    example_temp = content[2] if type(content[2]) == list else [content[2]]
                """
                for ex in example_temp:
                    ex.replace("→", "->")
                """
                function_res = {
                    "HTML": [html],
                    "Title": [feature_temp[0].split("→")[0].split("(")[0].strip()],
                    "Feature": feature_temp,
                    "Description": description_temp,
                    "Examples": example_temp,
                    "Category": [origin_category]
                }

                # 判断属于function还是operator
                # 只包含Operator：Operator
                # 只包含Function：Function，Function signature
                # 均包含：Function / Operator，Operator / Method，Predicate，Predicate / Value
                key_temp = feature_temp[0].split("→")[0].split("(")[0]
                if column_names[0] in ["Operator"]:
                    operators_dic[key_temp] = function_res
                elif column_names[0] in ["Function", "Function signature"]:
                    functions_dic[key_temp] = function_res
                else:
                    if "(" in str(feature_temp) and ")" in str(feature_temp):
                        functions_dic[key_temp] = function_res
                    else:
                        operators_dic[key_temp] = function_res

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
                    origin_category = sanitize_title(statement_key.split(".")[-1].strip())
                    # print(origin_category)
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


prefix = os.path.join("..","..","..","Feature Knowledge Base","Postgres")

Function_Htmls_Filename = os.path.join(prefix, "Functions", "HTMLs.json")
Function_dir_dicname = os.path.join(prefix, "Functions", "Results")
Function_Results_Category_Dicname = os.path.join(prefix, "Functions", "Results_Category")

Ops_Htmls_Filename = os.path.join(prefix, "Operators", "HTMLs.json")
Op_dir_dicname = os.path.join(prefix, 'Operators', 'Results')
Op_Results_Category_Dicname = os.path.join(prefix, "Operators", "Results_Category")

# crawler_results("function", Function_Htmls_Filename, Function_dir_dicname, Ops_Htmls_Filename, Op_dir_dicname)
# category_classifier(Function_dir_dicname, Function_Results_Category_Dicname)  # 文件写入方式为add
# category_classifier(Op_dir_dicname, Op_Results_Category_Dicname)  # 文件写入方式为add


print(column_names_temp)  # 统计所有的表格thead可能的情况
print(column_htmls_temp)
