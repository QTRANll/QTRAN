# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/22 23:17
# @Author  : zql
# @File    : HTMLs_Crawler_MySQL.py
# @Intro   : 获取MySQL的关于functions，operators和sql statements的所有htmls


import json
import os
from src.FeatureKnowledgeBase_Code.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


def htmls_crawler(html, dir_filename):
    if os.path.exists(dir_filename):
        print("文件 " + dir_filename + " 已存在！")
        return
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    statement_htmls = {}
    # 获取页面内id=docs-body的div标签内的所有链接元素
    soup_a = soup.find("div", id="docs-body").find("div", class_="toc").find_all("a")
    for item in soup_a:
        statement_htmls[item.text] = "https://dev.mysql.com/doc/refman/8.4/en/"+item.get("href")
        # 一级目录html则跳过，如果是二级目录html则继续访问该html并处理
        if item.text.count('.') == 1:
            continue

        driver.get(statement_htmls[item.text])
        WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
        soup_temp = BeautifulSoup(driver.page_source, "html.parser")
        soup_a_temp = soup_temp.find("div", id="docs-body").find("div", class_="toc")
        if soup_a_temp is None:
            continue
        else:
            soup_a_temp = soup_a_temp.find_all("a")
        for item_temp in soup_a_temp:
            statement_htmls[item_temp.text] = "https://dev.mysql.com/doc/refman/8.4/en/" + item_temp.get("href")

    with open(dir_filename, 'a', encoding='utf-8') as f:
        json.dump(statement_htmls, f, indent=4)


prefix = "../../../Feature Knowledge Base/MySQL/"
html_statements = "https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html"  # statements的目录页
dir_filename_statement = prefix + "SQL_Statements/SQL_Statements_HTMLs.json"
htmls_crawler(html_statements, dir_filename_statement)

html_func_op = "https://dev.mysql.com/doc/refman/8.4/en/functions.html"
dir_filename_fun_op = prefix + "Functions_and_Operators/Functions_and_Operators_HTMLs.json"  # functions 和 operators的目录页
htmls_crawler(html_func_op, dir_filename_fun_op)
