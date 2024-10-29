# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/24 10:23
# @Author  : zql
# @File    : Functions_and_Operators_Info_Crawler.py
# @Intro   : 获取MySQL的关于functions和operators的所有信息

import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag
from src.FeatureKnowledgeBase_Code.crawler_options import set_options

Functions_Categories = {
   "14.1": "Built-In Functions",
   "14.2": "Loadable Functions",
   "14.4.2": "Comparison Functions",
   "14.5": "Flow Control Functions",
   "14.6.2": "Mathematical Functions",
   "14.7": "Date and Time Functions",
   "14.8": "String Functions",
   "14.10": "Cast Functions",
   "14.11": "XML Functions",
   "14.12": "Bit Functions",
   "14.13": "Encryption and Compression Functions",
   "14.14": "Locking Functions",
   "14.15": "Information Functions",
   "14.16": "Spatial Analysis Functions",
   "14.17": "JSON Functions",
   "14.18": "Replication Functions",
   "14.19": "Aggregate Functions",
   "14.20": "Window Functions",
   "14.21": "Performance Schema Functions",
   "14.22": "Internal Functions",
   "14.23": "Miscellaneous Functions"
}


Operators_Categories = {
   "14.1": "Built-In Operators",
   "14.4.2": "Comparison Operators",
   "14.4.3": "Logical Operators",
   "14.4.4": "Assignment Operators",
   "14.6.1": "Arithmetic Operators",
   "14.8": "String Operators",
   "14.10": "Cast Operators",
   "14.12": "Bit Operators"
}


# 判断Tag是否为illustration：是则返回True，否则返回False
def is_illustration(tag_name, tag_class, tag_text):
    if tag_name == 'div' and 'titlepage' in tag_class:
        # 跳过标题
        return False
    elif tag_text == "":
        # 跳过空文本
        return False
    return True


# 获取illustration
def illustration_processor(soup_li_body):
    illustrations = []  # 存储处理的每一条illustration
    for item in soup_li_body.children:
        # 跳过非Tag
        if isinstance(item, Tag) == 0:
            continue

        item_name = item.name
        item_class = item.get("class")
        item_text = item.text
        # 跳过非illustration的Tag
        if not is_illustration(item_name, item_class, item_text):
            continue
        illustrations.append(item_text)

    return illustrations


def functions_and_operators_item_crawler(table_content):
    table_content_detailed = table_content
    table_content_detailed["HTML"] = [table_content["HTML"]]
    table_content_detailed["Title"] = [table_content["Title"]]

    if "(" in table_content_detailed["Name"] and ")" in table_content_detailed["Name"]:
        table_content_detailed["Type"] = "Function"
    else:
        table_content_detailed["Type"] = "Operator"
    table_content_detailed["Feature"] = ""
    table_content_detailed["Illustration"] = []
    table_content_detailed["Examples"] = []
    table_content_detailed["Category"] = []

    # 无相关链接信息，不进行爬取，则直接返回默认的值
    if table_content_detailed["Reference HTML"] == "":
        return table_content_detailed

    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(table_content_detailed["Reference HTML"])  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 查找出所有的class="listitem"的li标签
    soup_lis = soup.find_all("li", class_="listitem")

    if soup_lis is None:
        return table_content_detailed

    # 遍历li标签，确认li标签内是否包含name=Reference HTML末尾名称的a标签。如果包含则为要寻找的目标li标签
    # Reference HTML末尾名称
    a_name = table_content_detailed["Reference HTML"].split("#")[-1]
    for li in soup_lis:
        # 确认li标签内是否包含name=Reference HTML末尾名称的a标签
        a_first = li.find("a")
        # 如果包含则为要寻找的目标li标签
        if a_first and a_first.get("name") == a_name:
            # 读取feature，illustration，examples等信息
            # 获取feature：找到第一个class="link"的a标签，获取其text极为完整的feature值
            soup_a_link = li.find("a", class_="link")
            if soup_a_link:
                table_content_detailed["Feature"] = soup_a_link.text

            # 获取illustration
            table_content_detailed["Illustration"] = illustration_processor(li)

            # 获取examples：读取所有language-sql代码块儿文本（不包括终端的代码块language-terminal）
            code_blocks = li.findAll("code", class_="language-sql")
            # Example：包含分号的
            for block in code_blocks:
                if ";" in block.text:
                    table_content_detailed["Examples"].append(block.text)

            # 跳出循环
            break

    # 确认Category
    # 为functions和operators选择不同的category数组
    category_array = None
    if table_content_detailed["Type"] == "Function":
        category_array = Functions_Categories
    elif table_content_detailed["Type"] == "Operator":
        category_array = Operators_Categories

    title_index = table_content_detailed["Title"][0].split(' ')[0]
    for key_category, value_category in category_array.items():
        if key_category == title_index or key_category + "." in title_index:
            table_content_detailed["Category"].append(value_category)
    return table_content_detailed


# 爬取单个Reference Table Results文件中所有Functions/Operators的相关信息并返回
def functions_and_operators_table_crawler(reference_table_filename):
    with open(reference_table_filename, "r", encoding="utf-8") as rf:
        table_contents = json.load(rf)

    functions_and_operators_results = []
    functions_and_operators_results_exceptions = []
    # 遍历Reference Table Results文件中所有Functiosn/Operators，逐个爬取相关信息
    table_content_index = 0
    for table_content in table_contents:
        print(table_content["Title"])
        print(table_content["Name"])
        print(table_content["Reference HTML"])
        print("\n")

        try:
            table_content_detailed = functions_and_operators_item_crawler(table_content)
            functions_and_operators_results.append(table_content_detailed)
        except Exception as e:
            print("发生了异常：", e)
            table_content_detailed = table_content
            table_content_detailed["HTML"] = [table_content["HTML"]]
            table_content_detailed["Title"] = [table_content["Title"]]
            if "(" in table_content_detailed["Name"] and ")" in table_content_detailed["Name"]:
                table_content_detailed["Type"] = "Function"
            else:
                table_content_detailed["Type"] = "Operator"
            table_content_detailed["Feature"] = ""
            table_content_detailed["Illustration"] = []
            table_content_detailed["Examples"] = []
            table_content_detailed["Category"] = []
            functions_and_operators_results.append(table_content_detailed)
            functions_and_operators_results_exceptions.append(table_content_index)

        print(str(table_content_index)+'/'+str(len(table_contents))+'\n')
        table_content_index = table_content_index + 1

    return functions_and_operators_results, functions_and_operators_results_exceptions


def repair_exceptions(prefix_str):
    results_dicname = prefix_str+"Functions_and_Operators/Functions_Results"
    exceptions_dicname = prefix_str+"Functions_and_Operators/Functions_and_Operators_Results_Exceptions"
    repairments_dicname = prefix_str+"Functions_and_Operators/Functions_and_Operators_Results_Repairments"
    exceptions_filenames = os.listdir(exceptions_dicname)

    for filename in exceptions_filenames:
        print(filename)
        if os.path.exists(repairments_dicname + '/' + filename):
            continue
        repairments = []
        with open(exceptions_dicname + '/' + filename, "r", encoding="utf-8") as rf:
            exception_indexes = json.load(rf)
        with open(results_dicname + '/' + filename, "r", encoding="utf-8") as rf:
            results = json.load(rf)

        for index in exception_indexes:
            print(results[index])
            table_content_detailed = functions_and_operators_item_crawler(results[index])
            # results[index] = table_content_detailed
            table_content_detailed["index"] = index
            repairments.append(table_content_detailed)

        with open(repairments_dicname + '/' + filename, 'a', encoding='utf-8') as f:
            json.dump(repairments, f, indent=4)
        print('--------------------------')


def functions_and_operators_crawler(reference_table_dicname, results_dicname, exc_dicname):
    reference_table_filenames = os.listdir(reference_table_dicname)
    for filename in reference_table_filenames:
        print(reference_table_dicname + '/' + filename)
        print("\n")

        dir_filename = results_dicname + '/' + filename
        exc_dir_filename = exc_dicname + '/' + filename
        if os.path.exists(dir_filename):
            continue
        functions_and_operators_results, functions_and_operators_results_exceptions = functions_and_operators_table_crawler(reference_table_dicname + '/' + filename)
        with open(dir_filename, 'a', encoding='utf-8') as f:
            json.dump(functions_and_operators_results, f, indent=4)
        if len(functions_and_operators_results_exceptions) > 0:
            with open(exc_dir_filename, 'a', encoding='utf-8') as f:
                json.dump(functions_and_operators_results_exceptions, f, indent=4)
        print('--------------------------')


prefix = "../../../Feature Knowledge Base/MySQL/"
Reference_Table_Dicname = prefix + "Functions_and_Operators/Reference_Table_Results"
Results_Dicname = prefix + "Functions_and_Operators/Functions_Results"
Exc_dicname = prefix+"Functions_and_Operators/Functions_and_Operators_Results_Exceptions"
functions_and_operators_crawler(Reference_Table_Dicname, Results_Dicname, Exc_dicname)
