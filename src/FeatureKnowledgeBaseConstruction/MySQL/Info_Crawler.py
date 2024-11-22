# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/24 10:23
# @Author  : zql
# @File    : Info_Crawler.py
# @Intro   : 获取MySQL的关于functions和operators的所有信息
import json
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag
from src.Tools.Crawler.crawler_options import set_options
from src.Tools.Crawler.crawler_options import sanitize_title

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

def functions_and_operators_item_crawler(table_content, feature_type):
    table_content_detailed = table_content
    table_content_detailed["HTML"] = [table_content["HTML"]]
    table_content_detailed["Title"] = [table_content["Title"]]

    table_content_detailed["Feature"] = []
    table_content_detailed["Description"] = []
    table_content_detailed["Examples"] = []
    table_content_detailed["Category"] = table_content["Category"]

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
            soup_p_link = li.find("p")
            soup_a_link = soup_p_link.find_all("a", class_="link")
            if soup_a_link:
                for item in soup_a_link:
                    table_content_detailed["Feature"].append(item.text)
            # 获取illustration
            table_content_detailed["Description"] = illustration_processor(li)
            # 获取examples：读取所有language-sql代码块儿文本（不包括终端的代码块language-terminal）
            code_blocks = li.findAll("code", class_="language-sql")
            # Example：包含分号的
            for block in code_blocks:
                if ";" in block.text:
                    table_content_detailed["Examples"].append(block.text)
            # 跳出循环
            break
    return table_content_detailed

# 爬取单个Reference Table Results文件中所有Functions/Operators的相关信息并返回
def functions_and_operators_table_crawler(reference_table_filename, dic_path):
    with open(reference_table_filename, "r", encoding="utf-8") as rf:
        table_contents = json.load(rf)
    # 遍历Reference Table Results文件中所有Functiosn/operator，逐个爬取相关信息
    for index in range(len(table_contents)):
        table_content = table_contents[index]
        try:
            table_content_type = "function" if "(" in table_content["Name"] and ")" in table_content["Name"] else "operator"
            direct_filename = os.path.join(dic_path, str(index) + ".json")
            if os.path.exists(direct_filename):
                print(direct_filename + ":已存在")
                continue
            table_content_detailed = functions_and_operators_item_crawler(table_content, table_content_type)
            with open(direct_filename, "w", encoding="utf-8") as w:
                json.dump(table_content_detailed, w, indent=4)
        except Exception as e:
            print("发生了异常：", e)

def data_types_crawler(htmls_filename, dic_path):
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        contents = json.load(rf)
    index = 0
    for key, value in contents.items():
        result_file = os.path.join(dic_path, str(index)+".json")
        if os.path.exists(result_file):
            continue
        key_index = key.split(' ')[0]
        if key_index.count('.') == 1 or "syntax" in key.lower() or "type" not in key.lower():
            continue
        detailed ={
            "HTML": [value],
            "Title": [key],
            "Feature": [key],
            "Description": [],
            "Examples": [],
            "Category": [sanitize_title(key.split(' ',1)[-1])]
        }
        timeout = 5  # 等待时间
        options = set_options()
        driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
        driver.get(value)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
        WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
        soup = BeautifulSoup(driver.page_source, "html.parser")
        soup_docs = soup.find("div", id="docs-body")
        for item in soup_docs:
            if len(item.text.strip()):
                detailed["Description"].append(item.text)
        code_blocks = soup_docs.findAll("code", class_="language-sql")
        for item in code_blocks:
            if len(item.text.strip()):
                detailed["Examples"].append(item.text)
        with open(result_file, "w", encoding='utf-8') as w:
            json.dump(detailed, w, indent=4)
        index = index + 1