import json
import os
from src.Tools.Crawler.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


def statements_htmls_crawler(html, dir_filename):
    # 爬取TiDB的sql statements的htmls，分类别爬取
    statements_list = {}
    if len(html) == 0 or os.path.exists(dir_filename):
        return

    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    soup_div = soup.find("div", class_="markdown-body MuiBox-root css-0")
    # 遍历div的内容并记录文本内容
    soup_h2s = soup_div.find_all("h2")
    soup_tables = soup_div.find_all("table")
    for index in range(len(soup_h2s)):
        list_temp = {}
        soup_h2 = soup_h2s[index]
        soup_table = soup_tables[index]
        statement_category = soup_h2.text.strip()
        # 处理table内所有链接
        for soup_tr in soup_table.find("tbody").find_all("tr"):
            soup_td_first = soup_tr.find("td")
            soup_td_name = soup_td_first.text.strip()
            soup_td_html = "https://docs.pingcap.com/" + soup_td_first.find("a").get("href")
            list_temp[soup_td_name] = soup_td_html
        print(statement_category)
        statements_list[statement_category] = list_temp
        print("---------")
    with open(dir_filename, 'w', encoding='utf-8') as f:
        json.dump(statements_list, f, indent=4, ensure_ascii=False)


def operators_htmls_crawler(html, dir_filename):
    operators_list = {}
    if len(html) == 0 or os.path.exists(dir_filename):
        return

    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 查找到页面内所有的table
    soup_tables = soup.find_all("table")
    # 四个table的类别分别定为如下
    tables_category = ["No Category", "比较方法和操作符", "逻辑操作符", "赋值操作符"]
    # 分别处理四个table
    for index in range(len(tables_category)):
        list_temp = {}
        soup_table = soup_tables[index]
        table_category = tables_category[index]
        soup_body = soup_table.find("tbody") if soup_table else None
        soup_trs = soup_body.find_all("tr")
        # 遍历table内所有tr
        for soup_tr in soup_trs:
            soup_td_first = soup_tr.find("td")
            name = soup_td_first.text
            list_temp[name] = soup_td_first.find("a").get("href")
        operators_list[table_category] = list_temp
    with open(dir_filename, 'w', encoding='utf-8') as f:
        json.dump(operators_list, f, indent=4, ensure_ascii=False)


def functions_htmls_crawler(category, html, dir_filename):
    functions_list = {}
    results_list = {}
    if len(html) == 0 or os.path.exists(dir_filename):
        return

    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 查找到页面内所有的table
    soup_tables = soup.find_all("table")
    # 分别处理所有的table
    for index in range(len(soup_tables)):
        soup_table = soup_tables[index]
        soup_thead = soup_table.find("thead")
        # 判断table是否为functions相关的：判断thead中是否包含字符串"函数名"，如果不包含则跳过该table
        if "函数名" not in soup_thead.text:
            continue
        table_category = category  # 确定table类别
        soup_body = soup_table.find("tbody") if soup_table else None
        soup_trs = soup_body.find_all("tr")
        # 遍历table内所有tr
        for soup_tr in soup_trs:
            soup_td_first = soup_tr.find("td")
            name = soup_td_first.text
            functions_list[name] = soup_td_first.find("a").get("href")
    results_list[category] = functions_list
    with open(dir_filename, 'w', encoding='utf-8') as w:
        json.dump(results_list, w, indent=4)



prefix = "../../../Feature Knowledge Base/MariaDB/"
statements_html = "https://docs.pingcap.com/zh/tidb/stable/sql-statement-overview"
statements_htmls_dir_filename = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB', 'SQL_Statements', 'SQL_Statements_HTMLs.json')
statements_htmls_crawler(statements_html, statements_htmls_dir_filename)


operators_html = "https://docs.pingcap.com/zh/tidb/stable/operators"
operators_htmls_dir_filename = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB', 'Operators', 'HTMLs.json')
operators_htmls_crawler(operators_html, operators_htmls_dir_filename)


# 获取所有的类别对应的html
Functions_Htmls_Filename = "../../../Feature Knowledge Base/TiDB/Functions/Functions_HTMLs.json"
tabel_categories = [
    'Mathematical Functions', 'Date and Time Functions', 'Locking Functions', 'Aggregate Functions'
]
with open(Functions_Htmls_Filename, "r", encoding="utf-8") as r:
    functions_htmls = json.load(r)
# 爬取页面内以表格形式列出的name和对应html（html指向mysql官方文档）
for category in tabel_categories:
    if os.path.exists(os.path.join("../../../Feature Knowledge Base/TiDB/Functions", "Functions_HTMLs_" + category + '.json')):
        print("文件 " + category +".jsonl "+ " 已存在！")
        continue
    htmls = functions_htmls[category]  # 获取具体某个functions类别的相关html列表（html可能不止一个）
    for html in htmls:
        print(category)
        print(html)
        print("-----------------------")
        functions_htmls_dir_filename = os.path.join('..', '..', '..', 'Feature Knowledge Base', 'TiDB',
                                                     'Functions', 'Functions_HTMLs_'+category+'.json')
        functions_htmls_crawler(category, html, functions_htmls_dir_filename)
