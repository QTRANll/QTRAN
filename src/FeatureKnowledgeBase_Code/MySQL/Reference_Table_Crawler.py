# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 16:07
# @Author  : zql
# @File    : SReference_Table_Crawler.py
# @Intro   : 获取MySQL的关于functions和operators的Reference table信息：Name，Description，Reference html,Title,HTML

import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from src.FeatureKnowledgeBase_Code.crawler_options import set_options


# 爬取单个Functions and Operators页面内的Reference Table内容并存储
def reference_table_item_crawler(key, value, dic_name):
    dir_filename = dic_name + key + ".json"
    if os.path.exists(dir_filename):
        print("文件 " + dir_filename + " 已存在！")
        return
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(value)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    reference_table = []
    # 获取页面内第一个class=table的div标签元素
    soup_table = soup.find("div", class_="table")
    if soup_table:
        # 页面内存在class=table的Table：具体判断这第一个表格是否为Reference Table
        # 获取该div结构内的第一个class为table-contents的div标签元素
        soup_table_contents = soup_table.find("div", class_="table-contents")
        # 获取table-contents中的thead标签元素
        soup_table_thead = soup_table_contents.find("thead")
        # 判断是否为Reference Table
        if "Name" in soup_table_thead.text and "Description" in soup_table_thead.text:
            # 是Reference Table：获取table-contents中的tbody标签元素
            soup_table_tbody = soup_table_contents.find("tbody")
            # 获取tbody中的所有tr并读取数据
            soup_table_trs = soup_table_tbody.find_all("tr")
            for item in soup_table_trs:
                table_item = {"HTML": value, "Title": key, "Name": "", "Description": "", "Reference HTML": ""}
                item_texts = item.text.strip().split('\n')
                table_item["Name"] = item_texts[0].strip()
                table_item["Description"] = item_texts[2].strip()
                if item.find("a"):
                    table_item["Reference HTML"] = "https://dev.mysql.com/doc/refman/8.4/en/"+item.find("a").get("href")

                reference_table.append(table_item)

    with open(dir_filename, 'w', encoding='utf-8') as f:
        json.dump(reference_table, f, indent=4)


def reference_tables_crawler(htmls_filename, dic_name):
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
    for key_title, value_html in html_contents.items():
        print(key_title)
        print(value_html)
        print('-----------------')
        reference_table_item_crawler(key_title, value_html, dic_name)


prefix = "../../../Feature Knowledge Base/MySQL/"
Htmls_Filename = prefix + "Functions_and_Operators/Functions_and_Operators_HTMLs.json"
Dic_Name = prefix + "Functions_and_Operators/Reference_Table_Results/"
reference_tables_crawler(Htmls_Filename, Dic_Name)
