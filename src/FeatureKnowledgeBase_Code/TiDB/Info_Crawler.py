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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag
import re
from src.FeatureKnowledgeBase_Code.crawler_options import set_options

html_category_map = {
    'mathematical-functions': "Mathematical Functions",
    'date-and-time-functions': "Date and Time Functions",
    'locking-functions': "Locking Functions",
    'aggregate-functions': "Aggregate Functions",
    'logical-operators': "Logical Operators",
    'comparison-operators': "Comparison Operators",
    'assignment-operators': "Assignment Operators",
    'cast-functions': "Cast Operators",
    'bit-functions': "Bit Operators",
    'flow-control-functions': "",
    'arithmetic-functions': "Arithmetic Operators",
    'string-comparison-functions': "String Operators",
    'regexp': "String Operators"
}


def is_illustration(tag_name, tag_class, tag_text):
    if tag_text == "":
        #  跳过空文本
        return False
    return True

# 定义非法字符的替换规则
def sanitize_title(title):
    title = re.sub(r'<', 'less', title)
    title = re.sub(r'>', 'greater', title)
    title = re.sub(r':', 'colon', title)
    title = re.sub(r'\*', 'star', title)
    title = re.sub(r'[\/\\|?]', '_', title)  # 其他非法字符替换为下划线
    return title


def sql_statements_crawler(origin_category, title, html, results_dic):
    if os.path.exists(os.path.join(results_dic, sanitize_title(title) + '.json')):
        print("文件 " + os.path.join(results_dic, sanitize_title(title) + '.json') + " 已存在！")
        return

    result = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 获取statements相关文档信息的div块
    soup_div = soup.find("div", class_="markdown-body MuiBox-root css-0")
    if not soup_div:
        return
    # 获取html
    result["HTML"] = html
    # 获取SQL Statement Title
    result["Title"] = soup_div.find("h1").text if soup_div.find("h1") else ""
    print(result["Title"])
    # 获取SQL Statement Feature(语法图的代码部分)
    soup_syntax = soup_div.find("div", class_="syntax-diagram-module--root--vJoVV")
    if not soup_syntax:
        return
    result["Feature"] = [soup_syntax.find("pre").text] if soup_syntax.find("pre") else []
    result["Description"] = []

    # 获取statements“示例”模块中的所有examples
    subtitle_indexes = []
    doc_items = []
    pre_items = []
    example_doc_start_index = None
    for item in soup_div.children:
        #  跳过非Tag
        if isinstance(item, Tag) == 0:
            continue
        # 获取每个文本块的类型信息
        item_name = item.name
        item_class = item.get("class")  # 注意：item_class是列表形式的
        item_id = item.get("id").strip() if item.get("id") else ""
        item_text = item.text
        #  跳过非有效文本内容的Tag
        if not is_illustration(item_name, item_class, item_text):continue

        if item_id == "示例" and item_name == "h2":
            example_doc_start_index = len(doc_items)

        #  如果是SubTitle，则记录下标
        if item_name == 'h2': subtitle_indexes.append(len(doc_items))
        if item_name == 'pre':
            pre_items.append(item_text)
        else:
            pre_items.append("")
        doc_items.append(item_text)

    if not example_doc_start_index:
        return
    result["Description"] = doc_items[1:subtitle_indexes[0]]
    if example_doc_start_index in subtitle_indexes:
        example_doc_end_index = subtitle_indexes[subtitle_indexes.index(example_doc_start_index)+1] if (len(subtitle_indexes)-1) >= subtitle_indexes.index(example_doc_start_index)+1 else len(doc_items)
    else:
        example_doc_end_index = len(doc_items)
    result["Examples"] = []
    for index in range(example_doc_start_index, example_doc_end_index):
        if doc_items[index] != "" and ";" in doc_items[index]:
            result["Examples"].append(doc_items[index])

    result["Category"] = [origin_category]

    with open(os.path.join(results_dic, sanitize_title(title) + '.json'), 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

def statements_crawler_results(htmls_filename, results_dic):
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
        # 遍历statement的所有类别
        for category_key, value in html_contents.items():
            # 遍历各个类别下的所有htmls
            for statement_key, statement_value in value.items():
                print(statement_key+":"+str(statement_value))
                sql_statements_crawler(category_key, statement_key, statement_value, results_dic)
                print('----------------------')

def operators_crawler(origin_category, title, html, results_category_dicname, mysql_results_dic):
    html_new = html.replace("8.0", "8.4")  # 修改html中的版本信息为mysql8.4
    # 根据html中的operator类别字段，映射到对应的mysql的operators文件名
    matches = re.findall(r'/([^/#]+)\.html#', html_new)
    if len(matches) == 0:
        return
    else:
        html_category = matches[0]
    if not os.path.exists(os.path.join(mysql_results_dic, html_category_map[html_category]+".json")):
        return

    # 从mysql8.4的对应类别信息中查找到所需信息：以html_new作为查找的key
    with open(os.path.join(mysql_results_dic, html_category_map[html_category]+".json"), "r", encoding="utf-8") as r:
        mysql_operators = json.load(r)
    for key, value in mysql_operators.items():
        if html_new == value["Reference HTML"]:
            # 修改value的内容
            value_new = {
                "HTML": value["Reference HTML"],
                "Title": value["Name"],
                "Feature": value["Feature"],
                "Description": [value["Description"]] + value["Illustration"],
                "Examples": value["Examples"],
                "Category": [html_category_map[html_category]]
            }

            with open(os.path.join(results_category_dicname, html_category_map[html_category]+".jsonl"), "a", encoding="utf-8") as w:
                json.dump(value_new, w)
                w.write('\n')

    """
    # 依次检索mysql8.4的所有operators信息
    mysql_operators_filenames = os.listdir(mysql_results_dic)
    for filename in mysql_operators_filenames:
        with open(os.path.join(mysql_results_dic, filename), "r", encoding="utf-8") as r:
            mysql_operators = json.load(r)
        for key, value in mysql_operators.items():
            if html_new == value["Reference HTML"]:
                # 修改value的内容
                value_new = {
                    "HTML": value["Reference HTML"],
                    "Title": value["Name"],
                    "Feature": value["Feature"],
                    "Description": [value["Description"]] + value["Illustration"],
                    "Examples": value["Examples"],
                    "Category": value["Category"]
                }
                with open(results_filename, "a", encoding="utf-8") as w:
                    json.dump(value_new, w)
                    w.write('\n')
    """
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

def operators_category_classifier(results_filename, results_category_dicname):
    with open(results_filename, "r", encoding="utf-8") as r:
        lines = r.readlines()
    for line in lines:
        operator_line = json.loads(line)
        for category in operator_line["Category"]:
            with open(os.path.join(results_category_dicname, category+".jsonl"), "a", encoding="utf-8") as w:
                json.dump(operator_line, w)
                w.write('\n')


def operators_crawler_results(htmls_filename, results_category_dicname,  mysql_results_dic):
    # 获取所有operators的信息：从已爬取好的mysql8.4中检索，以reference html作为key进行检索（注：TiDB的operators链接中，需要将8.0修改为8.4）
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
    # 获取所有(name,html)
    operators_name_html = {}
    for category_key, value in html_contents.items():
        # 遍历各个类别下的所有htmls
        for statement_key, statement_value in value.items():
            print(statement_key + ":" + str(statement_value))
            operators_crawler(category_key, statement_key, statement_value, results_category_dicname, mysql_results_dic)
            print('----------------------')


def functions_crawler_results_h2(category, html, results_category_dicname):
    # 以h2作为标题划分各个函数信息
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
    subtitle_indexes = []  # 所有h2的index
    subtitle_hrefs = []  # 所有h2的对应链接
    pre_indexes = []  # 所有pre类型代码块的下标
    doc_items = []  # 所有文档内容的txt

    for item in soup_div.children:
        #  跳过非Tag
        if isinstance(item, Tag) == 0:
            continue
        # 获取每个文本块的类型信息
        item_name = item.name
        item_class = item.get("class")  # 注意：item_class是列表形式的
        item_id = item.get("id").strip() if item.get("id") else ""
        item_text = item.text
        #  跳过非有效文本内容的Tag
        if not is_illustration(item_name, item_class, item_text):continue

        #  如果是SubTitle，则记录下标
        if item_name == 'h2' and item_text not in ["Cast 函数和操作符表", "MySQL 兼容性", "另请参阅", "另请参考"]:
            subtitle_indexes.append(len(doc_items))
            subtitle_hrefs.append(html+item.find("a").get("href"))
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

        result_temp["HTML"] = subtitle_hrefs[subtitle_indexes.index(subtitle_index)]
        result_temp["Title"] = doc_items[subtitle_index]
        result_temp["Feature"] = [doc_items[subtitle_index]]  # 默认值为标题
        result_temp["Description"] = []
        result_temp["Examples"] = []
        description_end_flag = False
        for doc_index in range(docs_start_index, docs_end_index):
            if "示例" in doc_items[doc_index]:
                description_end_flag = True
            if not description_end_flag:
                result_temp["Description"].append(doc_items[doc_index])
            if doc_index in pre_indexes and ";" in doc_items[doc_index]:
                result_temp["Examples"].append(doc_items[doc_index])

        result_temp["Category"] = [category]
        with open(os.path.join(results_category_dicname, category + '.jsonl'), 'a', encoding='utf-8') as w:
            json.dump(result_temp, w, ensure_ascii=False)
            w.write('\n')


def functions_crawler_results_h3(category, html, results_category_dicname):
    # 以h3作为标题划分各个函数信息
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
    subtitle_indexes = []  # 所有h2的index
    subtitle_hrefs = []  # 所有h2的对应链接
    pre_indexes = []  # 所有pre类型代码块的下标
    doc_items = []  # 所有文档内容的txt
    h2_flag = False  # h2尚未出现

    for item in soup_div.children:
        #  跳过非Tag
        if isinstance(item, Tag) == 0:
            continue
        # 获取每个文本块的类型信息
        item_name = item.name
        item_class = item.get("class")  # 注意：item_class是列表形式的
        item_id = item.get("id").strip() if item.get("id") else ""
        item_text = item.text
        #  跳过非有效文本内容的Tag
        if not is_illustration(item_name, item_class, item_text):continue
        if item_name == 'h2':
            if h2_flag:
                break
            else:
                h2_flag = True
        #  如果是SubTitle，则记录下标
        if item_name == 'h3' and item_text not in ["Cast 函数和操作符表", "MySQL 兼容性", "另请参阅", "另请参考"]:
            subtitle_indexes.append(len(doc_items))
            subtitle_hrefs.append(html+item.find("a").get("href"))
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

        result_temp["HTML"] = subtitle_hrefs[subtitle_indexes.index(subtitle_index)]
        result_temp["Title"] = doc_items[subtitle_index]
        result_temp["Feature"] = [doc_items[subtitle_index]]  # 默认值为标题
        result_temp["Description"] = []
        result_temp["Examples"] = []
        description_end_flag = False
        for doc_index in range(docs_start_index, docs_end_index):
            if "示例" in doc_items[doc_index]:
                description_end_flag = True
            if not description_end_flag:
                result_temp["Description"].append(doc_items[doc_index])
            if doc_index in pre_indexes and ";" in doc_items[doc_index]:
                result_temp["Examples"].append(doc_items[doc_index])

        result_temp["Category"] = [category]
        with open(os.path.join(results_category_dicname, category + '.jsonl'), 'a', encoding='utf-8') as w:
            json.dump(result_temp, w, ensure_ascii=False)
            w.write('\n')


def functions_crawler(origin_category, title, html, results_category_dicname, mysql_results_dic):
    # 修改html中的版本信息为mysql8.4
    html_new = html.replace("8.0", "8.4")
    # 根据html中的function类别字段，映射到对应的mysql的functions文件名
    matches = re.findall(r'/([^/#]+)\.html#', html_new)
    if len(matches) == 0:
        return
    else:
        html_category = matches[0]

    # 从mysql8.4的function对应类别信息中查找到所需信息：以html_new作为查找的key
    with open(os.path.join(mysql_results_dic, html_category_map[html_category]+".json"), "r", encoding="utf-8") as r:
        mysql_functions = json.load(r)
    for key, value in mysql_functions.items():
        if html_new == value["Reference HTML"]:
            # 修改value的内容
            value_new = {
                "HTML": value["Reference HTML"],
                "Title": value["Name"],
                "Feature": value["Feature"],
                "Description": [value["Description"]] + value["Illustration"],
                "Examples": value["Examples"],
                "Category": [html_category_map[html_category]]
            }

            with open(os.path.join(results_category_dicname, html_category_map[html_category]+".jsonl"), "a", encoding="utf-8") as w:
                json.dump(value_new, w)
                w.write('\n')



def functions_crawler_results(functions_htmls_filename, results_category_dicname, mysql_results_dic):
    keys = ['Flow Control Functions', 'String Functions', 'Mathematical Functions', 'Date and Time Functions',
            'Bit Functions', 'Cast Functions', 'Encryption and Compression Functions', 'Locking Functions',
            'Information Functions', 'JSON Functions', 'Aggregate Functions', 'Window Functions', 'Sequence Functions',
            'TiDB Specific Functions', 'Miscellaneous Functions']
    # 为functions的官方文档界面分以下四种
    h2_categories = [
        'Flow Control Functions', 'Cast Functions', 'JSON Functions', 'Window Functions', 'Sequence Functions', 'TiDB Specific Functions'
    ]
    h3_categories = [
        'String Functions', 'Encryption and Compression Functions', 'Information Functions', 'Miscellaneous Functions'
    ]
    tabel_categories = [
        'Mathematical Functions', 'Date and Time Functions', 'Locking Functions', 'Aggregate Functions'
    ]
    manual_categories = [
        'Bit Functions'
    ]
    # 获取所有的类别对应的html
    with open(functions_htmls_filename, "r", encoding="utf-8") as r:
        functions_htmls = json.load(r)
    for category in h2_categories:
        if os.path.exists(os.path.join(results_category_dicname, category + '.jsonl')):
            print("文件 " + os.path.join(results_category_dicname, category + '.jsonl') + " 已存在！")
            continue
        htmls = functions_htmls[category]  # 获取具体某个functions类别的相关html列表（html可能不止一个）
        for html in htmls:
            print(category)
            print(html)
            print("-----------------------")
            functions_crawler_results_h2(category, html, results_category_dicname)

    for category in h3_categories:
        if os.path.exists(os.path.join(results_category_dicname, category + '.jsonl')):
            print("文件 " + os.path.join(results_category_dicname, category + '.jsonl') + " 已存在！")
            continue
        htmls = functions_htmls[category]  # 获取具体某个functions类别的相关html列表（html可能不止一个）
        for html in htmls:
            print(category)
            print(html)
            print("-----------------------")
            functions_crawler_results_h3(category, html, results_category_dicname)

    for category in tabel_categories:
        # 判断文件是否已经存在
        if os.path.exists(os.path.join(results_category_dicname, category + '.jsonl')):
            print("文件 " + os.path.join(results_category_dicname, category + '.jsonl') + " 已存在！")
            continue
        # 读取已获取的functions table的htmls
        functions_htmls_dir_filename = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB',
                                                    'Functions', 'Functions_HTMLs_' + category + '.json')

        # 获取所有operators的信息：从已爬取好的mysql8.4中检索，以reference html作为key进行检索（注：TiDB的operators链接中，需要将8.0修改为8.4）
        with open(functions_htmls_dir_filename, "r", encoding="utf-8") as rf:
            html_contents = json.load(rf)
        # 遍历statement的所有类别
        for category_key, value in html_contents.items():
            # 遍历各个类别下的所有htmls
            for function_key, function_value in value.items():
                print(function_key + ":" + str(function_value))
                functions_crawler(category_key, function_key, function_value, results_category_dicname, mysql_results_dic)
                print('----------------------')


prefix = "../../../Feature Knowledge Base/TiDB/"

# 爬取statement的每个页面的信息并存储
Statements_Htmls_Filename = prefix + "SQL_Statements/SQL_Statements_HTMLs.json"
Statements_Results_Dicname = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB', 'SQL_Statements', 'SQL_Statements_Results')
Statements_Results_Category_Dicname = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB', 'SQL_Statements', 'SQL_Statements_Results_Category')
# statements_crawler_results(Statements_Htmls_Filename, Statements_Results_Dicname)
# category_classifier(Statements_Results_Dicname, Statements_Results_Category_Dicname)


# operators：从已爬取好的mysql信息中，查找到对应的operators信息
Operators_Htmls_Filename = prefix + "Operators/Operators_HTMLs.json"
Operators_Results_Category_Dicname = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB', 'Operators', 'Operators_Results_Category')
Mysql_Operators_Results_Dicname = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'Mysql', 'Functions_and_Operators', 'Functions_and_Operators_Results_Category', 'Operators_Category')
# operators_crawler_results(Operators_Htmls_Filename, Operators_Results_Category_Dicname, Mysql_Operators_Results_Dicname)


# functions：分四种情况对functions的信息进行爬取
Functions_Htmls_Filename = prefix + "Functions/Functions_HTMLs.json"
Functions_Results_Category_Dicname = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB', 'Functions', 'Functions_Results_Category')
Mysql_Functions_Results_Dicname = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'Mysql', 'Functions_and_Operators', 'Functions_and_Operators_Results_Category', 'Functions_Category')
# functions_crawler_results(Functions_Htmls_Filename, Functions_Results_Category_Dicname, Mysql_Functions_Results_Dicname)


"""
# 修改sql statements结果的格式
dic_name = "../../../Feature Knowledge Base/TiDB/SQL_Statements/SQL_Statements_Results"
filenames = os.listdir(dic_name)
for filename in filenames:
    with open(os.path.join(dic_name, filename), "r", encoding="utf-8") as r:
        data = json.load(r)

    data["Feature"] = [data["Feature"]]

    with open(os.path.join(dic_name, filename), "w", encoding="utf-8") as w:
        json.dump(data, w, indent=4)
"""

"""
# 修改operators结果的格式
filename = "../../../Feature Knowledge Base/TiDB/Operators/Operators_Results/Operators_Results_temp.jsonl"
filename_modified = "../../../Feature Knowledge Base/TiDB/Operators/Operators_Results/Operators_Results.jsonl"
with open(filename, "r", encoding="utf-8") as r:
    lines = r.readlines()
for line in lines:
    data = json.loads(line)
    data["Feature"] = [data["Feature"]]
    with open(filename_modified, "a", encoding="utf-8") as w:
        json.dump(data, w)
        w.write('\n')
"""

