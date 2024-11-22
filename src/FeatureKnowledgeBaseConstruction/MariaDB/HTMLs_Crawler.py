import json
import os
from src.Tools.Crawler.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# 爬取Functions and Operators页面内的Reference Table的所有表格项并存储
def funcs_htmls_crawler(html_func_op, op_html_path, dir_filename_fun_op):
    ops_htmls = []
    with open(op_html_path, 'r', encoding='utf-8') as r:
        ops_htmls_contents = json.load(r)
    for key,value in ops_htmls_contents.items():
        for sub_key, sub_value in value.items():
            ops_htmls.append(sub_value)

    if os.path.exists(dir_filename_fun_op):
        print("文件 " + dir_filename_fun_op + " 已存在！")
        return
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html_func_op)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    reference_table = {}  # 用于存储所有的表项内容
    # 获取表格项
    soup_div = soup.find("div", class_="node creole")
    soup_table = soup_div.find("table")
    if soup_table:
        # 是Reference Table：获取table-contents中的tbody标签元素
        soup_table_tbody = soup_table.find("tbody")
        # 获取tbody中的所有tr并读取数据
        soup_table_trs = soup_table_tbody.find_all("tr")
        for item in soup_table_trs:
            # 获取tr中的所有td
            soup_table_tds = item.find_all("td")
            if len(soup_table_tds):
                # 第一个td，也就是第一列就是要读取的name和html
                soup_table_td_selected = soup_table_tds[0]
                html = urljoin(html_func_op, soup_table_td_selected.find("a").get("href")) if soup_table_td_selected.find("a") else ""
                if html in ops_htmls:
                    continue
                else:
                    reference_table[soup_table_td_selected.text] = html
    return {"No Category":reference_table}

def ops_htmls_crawler(html):
    ops_list = {}
    ops_htmls = []
    if len(html) == 0:
        return

    # 递归获取特定类别的statement的所有htmls
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 获取operators相关目录
    soup_section = soup.find("section", id="content").find("div")
    # 遍历div的内容并记录文本内容
    # soup_h3s = soup_section.find_all("h3")[:-1]
    soup_h3s = soup_section.find_all("h3")[:-1]
    soup_uls = soup_section.find_all("ul", class_="media-list listing embedded")
    for index in range(len(soup_h3s)):
        list_temp = {}
        soup_h3 = soup_h3s[index]
        soup_ul = soup_uls[index]
        op_category = soup_h3.text.strip()
        # 处理ul内所有链接
        for soup_li in soup_ul.children:
            if index == len(soup_h3s) - 1:
                # print(soup_h3)
                # print(soup_ul)
                print(soup_li)
            soup_a = soup_li.find("a")
            soup_h4 = soup_li.find("h4")
            if soup_a == -1:
                continue
            title = soup_h4.text.strip()
            html_temp = urljoin(html, soup_a.get("href"))
            if "overview" in title.lower():
                continue
            list_temp[title] = html_temp
            ops_htmls.append(html_temp)
        ops_list[op_category] = list_temp
        print("---------")
    return ops_list



