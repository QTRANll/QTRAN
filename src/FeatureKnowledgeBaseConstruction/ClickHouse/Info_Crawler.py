# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/28 10:16
# @Author  : shaocanfan
# @File    : Info_Crawler.py
# @Intro   :


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


#  处理functions，获取feature,description和examples:遍历处理Document Body的内容并获取feature,description和examples
def function_article_body_processor(category, title, html, dic_filename, soup_body, function_name_h_type):
    if not soup_body: return

    doc_items = []  # 存储处理文档中的每一条文本块
    function_subtitle_indexes = []  # 存储每个function的subtitle在数组中的下标
    code_indexes = []  # 存储每个代码块在illustrations数组中的下标

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
        if item_name == function_name_h_type:
            function_subtitle_indexes.append(len(doc_items))
        # 如果是code(可能是feature syntax，也可能是code)，则记录下标
        # code的class是['language-sql', 'codeBlockContainer_APcc', 'theme-code-block']
        if item_name == 'div' and 'language-sql' in item_class:
            code_indexes.append(len(doc_items))
        # 如果item内找到凑得，则将code存储
        doc_items.append(item_text.replace("\u200B", ""))
    # 遍历处理doc_items的内容，以subtitle的下标为function分界线处理所有的functions内容
    for i in range(len(function_subtitle_indexes)):
        # 获取当前所处理function信息的开始下标和结束下标：doc_items[start_index,end_index)
        start_index = function_subtitle_indexes[i]
        if i == len(function_subtitle_indexes) - 1:
            # i为subtitle_indexes的最后一个下标
            end_index = len(doc_items)
        else:
            end_index = function_subtitle_indexes[i + 1]

        # 处理当前所function：获取HTML,Title,Feature,Description,Examples,Category
        feature_info = {}
        feature_info["HTML"] = [html]
        feature_info["Title"] = [doc_items[start_index].replace("\u200B", "")]  # 当前处理function的title
        feature_info["Feature"] = feature_info["Title"]  # 先默认等于title，后续为有具体syntax code的function进行Feature的修改
        feature_info["Description"] = []
        feature_info["Examples"] = []
        feature_info["Category"] = [category]

        # 在doc_items[start_index,end_index)中查找第一个出现的syntax和example小标题的下标
        syntax_title_index = None
        example_title_index = None
        for t in range(start_index, end_index):
            # 在doc_items[start_index,end_index)中查找syntax的下标：text内容为Syntax，且限制长度（因为部分页面用的是syntax:格式）
            if "syntax" in doc_items[t].lower() and len(doc_items[t]) <= len("syntax") + 4:
                syntax_title_index = t
                break

        for t in range(start_index, end_index):
            # 在doc_items[start_index,end_index)中查找example小标题的下标：text内容为Examples, 且限制长度（因为部分页面用的是examples:格式）
            if "example" in doc_items[t].lower() and len(doc_items[t]) <= len("example") + 4:
                example_title_index = t
                break

        # Feature
        # 如果文本中有"syntax"：则syntax下标后紧接着的下一个code index被认为是feature语法
        # 如果文本中没有"syntax"：如果文本中有"example"分界线，则取example下标的前一个的code txt作为feature语法；如果文本中没有"example"分界线，则直接为默认值（用title作为feature语法）
        if syntax_title_index:
            for index_feature in range(start_index, end_index):
                if index_feature not in code_indexes:
                    continue
                if index_feature > syntax_title_index:
                    feature_info["Feature"] = [doc_items[index_feature]]
                    break
        else:
            if example_title_index:
                print("example_title_index:"+str(example_title_index))
                for index_feature in range(start_index, example_title_index):
                    if index_feature not in code_indexes:
                        continue
                    feature_info["Feature"] = [doc_items[index_feature]]
                    # 取第一个即可退出
                    break

        # Examples
        # 如果文本中有"example"分界线：则example_title_index之后的code index被认为全是feature examples
        # 如果文本中没有"example"分界线：则code index被认为全是feature examples
        if example_title_index:
            for index_example in range(start_index, end_index):
                if index_example not in code_indexes:
                    continue
                if index_example > example_title_index:
                    feature_info["Examples"].append(doc_items[index_example])
        else:
            for index_example in range(start_index, end_index):
                if index_example not in code_indexes:
                    continue
                feature_info["Examples"].append(doc_items[index_example])

        # feature description范围
        # 如果如果文本中有"example"分界线，从start_index到第一个example之间（粗略的将syntax也包含在description中）
        # 如果文本中无"example"分界线，则粗略认为所有text内容均为description
        if example_title_index:
            feature_info["Description"] = doc_items[start_index: example_title_index]
        else:
            feature_info["Description"] = doc_items[start_index: end_index]
        if syntax_title_index:
            print(doc_items[syntax_title_index])

        if example_title_index:
            print(doc_items[example_title_index])
        print("feature:"+str(feature_info["Feature"]))
        print("examples:" + str(feature_info["Examples"]))
        print('-------------------')

        # 存储function information
        try:
            file_cnt = len(os.listdir(dic_filename))
            with open(os.path.join(dic_filename, str(file_cnt) + ".json"), "w", encoding="utf-8") as w:
                json.dump(feature_info, w, indent=4)
        except Exception as e:
            # 文件名称不合法，将文件名称修改为合法的
            left_index = feature_info["Feature"][0].find("(")
            new_name = feature_info["Feature"][0]
            if left_index >= 0:
                new_name = feature_info["Feature"][0][:left_index]
            print(new_name)
            file_cnt = len(os.listdir(dic_filename))
            with open(os.path.join(dic_filename, str(file_cnt) + ".json"), "w", encoding="utf-8") as w:
                json.dump(feature_info, w, indent=4)
            print("存储文件时发生异常：" + str(e))

#  处理operators，获取feature,description和examples:遍历处理Document Body的内容并获取feature,description和examples
def operator_article_body_processor(category, title, html, dic_name, soup_body, op_category_h_type, op_name_h_type):
    if not soup_body:
        return

    doc_items = []  # 存储处理文档中的每一条文本块
    category_subtitle_indexes = []  # 存储每个op的类别subtitle在数组中的下标
    p_code_indexes = []  # 记录p标签txt的下标，该p标签内部包含code-code格式的信息
    name_subtitle_indexes = []  # 存储op的name在数组中的下标
    code_indexes = []  # 存储每个代码块在illustrations数组中的下标

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

        #  记录op的类别下标:op_category_h == "h2"
        if item_name == op_category_h_type:
            category_subtitle_indexes.append(len(doc_items))

        # 处理标签p
        if item_name == "p" and (" – " in item_text or " — " in item_text):
            code_blocks = item.find_all("code")
            if not code_blocks:
                pass

            # 获取op对应的function的信息，添加到op的description和examples中
            des_func = []
            exam_func = []
            func_name = code_blocks[-1].text.split('(')[0].strip() if len(code_blocks) > 1 else ""
            # 对应的function_dicname
            if len(func_name):
                function_dicname = dic_name.replace("operator", "function")
                filenames_func = os.listdir(function_dicname)
                for file in filenames_func:
                    if file.lower().split('.')[0] == func_name.lower() or file.lower().startswith(func_name.lower()+"("):
                        # 说明在function中找到了对应的函数
                        with open(os.path.join(function_dicname, file), "r", encoding="utf-8") as r:
                            function_content = json.load(r)
                        des_func = function_content["Description"]
                        exam_func = function_content["Examples"]

            # 查找到code了:处理当下的p，将信息存储到文件中
            op_result = {
                "HTML": [html],
                "Title": [code_blocks[0].text],
                "Feature": [
                    code_blocks[0].text
                ],
                "Description": [item_text] + des_func,
                "Examples": [] + exam_func,
                "Category": [
                    doc_items[category_subtitle_indexes[-1]]
                ]
            }
            p_code_indexes.append(len(doc_items))

            # 存储相关op信息
            file_cnt = len(os.listdir(dic_name))
            with open(os.path.join(dic_name, str(file_cnt) +".json"), "w", encoding="utf-8") as w:
                json.dump(op_result, w, indent=4)
        #  记录op的name下标:op_category_h == "h2"
        if item_name == op_name_h_type:
            name_subtitle_indexes.append(len(doc_items))

        # 如果是code(可能是feature syntax，也可能是code)，则记录下标
        # code的class是['language-sql', 'codeBlockContainer_APcc', 'theme-code-block']
        if item_name == 'div' and 'language-sql' in item_class:
            code_indexes.append(len(doc_items))
        doc_items.append(item_text.replace("\u200B", ""))

    # 遍历处理doc_items的内容，以category subtitle（h2）的下标为operator类别分界线
    # 遍历过程中
    for i in range(len(category_subtitle_indexes)):
        # print(doc_items[i])
        # 获取当前所处理op category的开始下标和结束下标：doc_items[start_index,end_index)
        start_index = category_subtitle_indexes[i]
        if i == len(category_subtitle_indexes) - 1:
            # i为subtitle_indexes的最后一个下标
            end_index = len(doc_items)
        else:
            end_index = category_subtitle_indexes[i + 1]

        # 处理当前op category下的所有op信息
        # 检查当前op category下是否包含<p>标签
        p_code_flag = False
        for index in range(start_index, end_index):
            if index in p_code_indexes:
                # 说明包含p，则该category已经处理完毕（在前面的遍历中）
                p_code_flag = True
                break
        # 说明不包含p，则对category内的信息进行类似于function的处理
        if not p_code_flag:
            # 以下的内容进行人工处理
            print(doc_items[category_subtitle_indexes[i]])

def function_crawler(origin_category, title, html, dic_filename):
    result = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_article = soup.find("article")
    soup_document_markdown = soup_article.find("div", class_="theme-doc-markdown markdown")

    # 获取当前页面的Categories:从页面上方的导航栏中提取
    soup_breadcrumb = soup_article.find("nav")
    soup_breadcrumb_list = []
    for soup_li in soup_breadcrumb.find_all("li"):
        if len(soup_li.text):
            soup_breadcrumb_list.append(soup_li.text)
    if soup_breadcrumb_list[1] == "Regular function":
        origin_category = soup_breadcrumb_list[2] + " function"
    elif soup_breadcrumb_list[1] in ["Aggregate function", "Table function", "Window function"]:
        origin_category = soup_breadcrumb_list[1]

    # 获取页面内h2标题的个数h2_cnt以及h3标题的个数h3_cnt
    """
    1. 以h2作为标题划分页面内多个函数，有一个h1上级标题（即页面顶部标题）：例如[Arithmetic function | clickhouse Docs](https://clickhouse.com/docs/en/sql-reference/functions/arithmetic-functions)
    2. 以h3作为标题划分页面内多个函数，有一个h2上级标题：例如[function for Working with Embedded Dictionaries | clickhouse Docs](https://clickhouse.com/docs/en/sql-reference/functions/ym-dict-functions)
    3. 页面内只有一个函数，Syntax和Example没有明确的划分：例如[arrayJoin function | clickhouse Docs](https://clickhouse.com/docs/en/sql-reference/functions/array-join)
    * 读取页面内所有h2标题个数h2_cnt和h3标题个数h3_cnt。
	* h2_cnt > 1，h3_cnt = 任意：情况1
	* h2_cnt = 1，h3_cnt = 0：情况1
	* h2_cnt = 1，h3_cnt != 0：情况2
	* h2_cnt = 0，h3_cnt = 任意：情况3
    """

    h2_cnt = len(soup.find_all("h2"))
    h3_cnt = len(soup.find_all("h3"))
    # 根据不同的页面类型分情况进行functions的信息爬取
    if h2_cnt > 1:
        # type 1
        function_article_body_processor(origin_category, title, html, dic_filename, soup_document_markdown, "h2")
    elif h2_cnt == 1:
        if h3_cnt:
            # type 2
            function_article_body_processor(origin_category, title, html, dic_filename, soup_document_markdown, "h3")
        else:
            # type 1
            function_article_body_processor(origin_category, title, html, dic_filename, soup_document_markdown, "h2")
    elif h2_cnt == 0:
        # type 3
        function_article_body_processor(origin_category, title, html, dic_filename, soup_document_markdown, "h1")


def op_crawler(origin_category, title, html, dic_filename):
    if title == "EXISTS":
        function_crawler("EXISTS operator", title, html, dic_filename)
        return
    elif title == "operator":
        # 下面的代码进行处理
        pass
    else:
        return
    result = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_article = soup.find("article")
    soup_document_markdown = soup_article.find("div", class_="theme-doc-markdown markdown")
    operator_article_body_processor(origin_category, title, html, dic_filename, soup_document_markdown, "h2", "h3")

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
    soup_article = soup.find("article")
    soup_document_markdown = soup_article.find("div", class_="theme-doc-markdown markdown")
    for item in soup_document_markdown:
        if len(item.text.strip()):
            detailed["Description"].append(item.text)

    soup_divs = soup_document_markdown.find_all("div")
    for item in soup_divs:
        if 'language-sql' in item.get('class') and len(item.text.strip()):
            detailed["Examples"].append(item.text)

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
                    function_crawler(category_key, statement_key, statement_value, dic_filename)
                elif feature_type == "operator":
                    op_crawler(category_key, statement_key, statement_value, dic_filename)
                elif feature_type == "datatype":
                    data_types_crawler(category_key, statement_key, statement_value, dic_filename)
                print('----------------------')


