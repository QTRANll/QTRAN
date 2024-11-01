import json
import os
from src.FeatureKnowledgeBase_Code.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag


# 爬取Functions and Operators页面内的Reference Table的所有表格项并存储
def funcs_ops_htmls_crawler(html, dir_filename_one, dir_filename_two):
    if os.path.exists(dir_filename_one) and os.path.exists(dir_filename_two):
        print("文件 " + dir_filename_one + "," + dir_filename_two + "已存在！")
        return
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作

    htmls_table = {}  # 用于存储所有的htmls
    # 要跳过的html
    skip_htmls = [
        "https://duckdb.org/docs/sql/functions/dateformat",
        "https://duckdb.org/docs/sql/functions/nested"
    ]

    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_lis = soup.find("div", class_="index").find_all("li")

    for soup_li in soup_lis:
        name = soup_li.text.strip()
        href = "https://duckdb.org" + soup_li.find("a").get("href")
        if href in skip_htmls:
            continue
        htmls_table[name] = href

    with open(dir_filename_one, 'w', encoding='utf-8') as f:
        json.dump({"No Category": htmls_table}, f, indent=4)

    with open(dir_filename_two, 'w', encoding='utf-8') as f:
        json.dump({"No Category": htmls_table}, f, indent=4)


prefix = "../../../Feature Knowledge Base/DuckDB/"
HTML = "https://duckdb.org/docs/sql/functions/overview"
dir_filename_fun_op = [
    prefix + "Functions/Functions_HTMLs.json",
    prefix + "Operators/Operators_HTMLs.json"
]

funcs_ops_htmls_crawler(HTML, dir_filename_fun_op[0], dir_filename_fun_op[1])


