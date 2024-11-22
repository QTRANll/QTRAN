# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/22 23:17
# @Author  : zql
# @File    : HTMLs_Crawler_MySQL.py
# @Intro   : Get all of mysql's htmls for data types, functions, operators
from src.Tools.Crawler.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def htmls_crawler(html):
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    statement_htmls = {}
    soup_a = soup.find("div", id="docs-body").find("div", class_="toc").find_all("a")
    for item in soup_a:
        statement_htmls[item.text] = html.rsplit('/', 1)[0] + "/" +item.get("href")
        if item.text.count('.') == 1: continue
        driver.get(statement_htmls[item.text])
        WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
        soup_temp = BeautifulSoup(driver.page_source, "html.parser")
        soup_a_temp = soup_temp.find("div", id="docs-body").find("div", class_="toc")
        if soup_a_temp is None:
            continue
        else:
            soup_a_temp = soup_a_temp.find_all("a")
        for item_temp in soup_a_temp:
            statement_htmls[item_temp.text] = urljoin(html, item_temp.get("href"))
    return statement_htmls





