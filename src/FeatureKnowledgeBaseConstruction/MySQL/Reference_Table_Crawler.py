# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 16:07
# @Author  : zql
# @File    : SReference_Table_Crawler.py
# @Intro   : 获取MySQL的关于functions和operators的Reference table信息：Name，Description，Reference html,Title,HTML

import json
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from src.Tools.Crawler.crawler_options import set_options
from urllib.parse import urljoin
Categories = {
   "14.1": "Built-In function and operator",
   "14.2": "Loadable function",
   "14.4.2": "Comparison function and operator",
   "14.5": "Flow Control function",
   "14.6.2": "Mathematical function",
   "14.7": "Date and Time function",
   "14.8": "String function and operator",
   "14.10": "Cast function and operator",
   "14.11": "XML function",
   "14.12": "Bit function and operator",
   "14.13": "Encryption and Compression function",
   "14.14": "Locking function",
   "14.15": "Information function",
   "14.16": "Spatial Analysis function",
   "14.17": "JSON function",
   "14.18": "Replication function",
   "14.19": "Aggregate function",
   "14.20": "Window function",
   "14.21": "Performance Schema function",
   "14.22": "Internal function",
   "14.23": "Miscellaneous function",
    "14.4.3": "Logical operator",
    "14.4.4": "Assignment operator",
    "14.6.1": "Arithmetic operator"
}
# 爬取单个Functions and Operators页面内的Reference Table内容并存储
def reference_table_item_crawler(key, value, dic_name):
    dir_filename = os.path.join(dic_name, key.split(" ")[0] + ".json")
    if os.path.exists(dir_filename):
        print("File " + dir_filename + " 已存在！")
        return
    timeout = 4  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(value)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    reference_table = []
    soup_table = soup.find("div", class_="table")
    if soup_table:
        # 页面内存在class=table的Table：具体判断这第一个表格是否为Reference Table
        # 获取该div结构内的第一个class为table-contents的div标签元素
        soup_table_contents = soup_table.find("div", class_="table-contents")
        soup_table_thead = soup_table_contents.find("thead")
        # 判断是否为Reference Table
        if "Name" in soup_table_thead.text and "Description" in soup_table_thead.text:
            # 是Reference Table：获取table-contents中的tbody标签元素
            soup_table_tbody = soup_table_contents.find("tbody")
            # 获取tbody中的所有tr并读取数据
            soup_table_trs = soup_table_tbody.find_all("tr")
            for item in soup_table_trs:
                table_item = {"HTML": value, "Title": key, "Name": "", "Description": "", "Reference HTML": "", "Category":""}
                item_texts = item.text.strip().split('\n')
                table_item["Name"] = item_texts[0].strip()
                table_item["Description"] = item_texts[2].strip()
                if item.find("a"):
                    table_item["Reference HTML"] = urljoin(value, item.find("a").get("href"))

                title_index = table_item["Title"].split(' ')[0]
                print(title_index)
                for key_category, value_category in Categories.items():
                    if key_category == title_index or key_category + "." in title_index:
                        table_item["Category"] = value_category
                reference_table.append(table_item)
    with open(dir_filename, 'w', encoding='utf-8') as f:
        json.dump(reference_table, f, indent=4)

def reference_tables_crawler(htmls_filename, dic_name):
    with open(htmls_filename, "r", encoding="utf-8") as rf:
        html_contents = json.load(rf)
    for key_title, value_html in html_contents.items():
        print(key_title+":"+value_html)
        reference_table_item_crawler(key_title, value_html, dic_name)



