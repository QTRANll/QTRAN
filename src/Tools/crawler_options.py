# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/22 17:47
# @Author  : zql
# @File    : crawler_options.py
# @Intro   : 爬虫的基本设置


from selenium.webdriver.chrome.options import Options
import re
import glob
import os
import json
def set_options():
    option = Options()
    option.page_load_strategy = 'eager'
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--disable-extensions")
    option.add_argument('--no-sandbox')
    option.add_argument('--ignore-certificate-errors')
    option.add_argument('--allow-running-insecure-content')
    #  配置headless模型:没有界面的模型，可以节省很多的内存和cpu占用，而且禁用了cpu渲染，提高加载速度。

    option.add_argument('--headless')  # 无头浏览器
    option.add_argument("--disable--gpu")  # 禁用显卡
    option.add_argument("--disable-software-rasterizer")
    #  配置不加载图片:图片通常在网络中加载消耗较多的时间，而且渲染较慢，如果不需要即时加载图片的话可以禁用图片加载
    option.add_argument("blink-settings=imagesEnabled=false")
    #  禁用插件加载
    option.add_argument('--disable-plugins')
    option.add_argument("--disable-extensions")
    return option

def sanitize_title(title):
    title = re.sub(r'<', ' less ', title)
    title = re.sub(r'>', ' greater ', title)
    title = re.sub(r':', ' colon ', title)
    title = re.sub(r'\*', ' multiply ', title)
    title = re.sub(r'\/', ' divide ', title)
    title = re.sub(r'\"', "'", title)
    title = re.sub(r'\n', " ", title)
    title = re.sub(r'[\\|?]', '_', title)  # 其他非法字符替换为下划线
    return title

def category_classifier(results_dicname, results_category_dicname):
    json_files = glob.glob(os.path.join(results_dicname, '*.json'))
    if len(os.listdir(results_category_dicname)):
        print("Category OK.")
        return
    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as r:
            data = json.load(r)
        # 将结果存储到对应的jsonl文件中,可能属于多个类别
        for category in data["Category"]:
            with open(os.path.join(results_category_dicname, category + ".jsonl"), "a",encoding="utf-8") as w:
                json.dump(data, w)
                w.write('\n')