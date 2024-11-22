import json
import os
from src.Tools.Crawler.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin

statements_category_htmls = {
    "Account Management SQL Commands":"https://mariadb.com/kb/en/account-management-sql-commands/",
    "Administrative SQL Statements":"https://mariadb.com/kb/en/administrative-sql-statements/",
    "Data Definition":"https://mariadb.com/kb/en/data-definition/",
    "Data Manipulation":"https://mariadb.com/kb/en/data-manipulation/",
    "Prepared Statements":"https://mariadb.com/kb/en/prepared-statements/",
    "Programmatic and Compound Statements":"https://mariadb.com/kb/en/programmatic-compound-statements/",
    "Stored Routine Statements":"https://mariadb.com/kb/en/stored-routine-statements/",
    "Table Statements":"https://mariadb.com/kb/en/table-statements/",
    "Transactions":"https://mariadb.com/kb/en/transactions/"
}

def get_statements_htmls_category(dir_filename, category, crawler_html):
    htmls_list = {}
    if len(crawler_html) == 0:
        return htmls_list

    # 递归获取特定类别的statement的所有htmls
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(crawler_html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 读取页面内列表中所有li元素
    soup_a = soup.find("ul", class_="media-list listing").find_all("li")
    for item in soup_a:
        # 获取得到li元素的class标签列表：['media', 'node', 'category', 'product', 'no_product_class']。
        # 其中含有category的为目录链接（连接内还有子项目），含有article的为文章链接（即为需要的html）
        class_list = item.get("class")
        if 'category' in class_list:
            # 目录链接:递归进行读取
            a = item.find("a")
            html_txt = "https://mariadb.com/" + a.get("href") if a else ""
            get_statements_htmls_category(dir_filename, category, html_txt)
        elif 'article' in class_list:
            # 获取文章链接及名称
            h4_name = item.find("h4")
            html_name = h4_name.text.strip() if h4_name else ""
            a = item.find("a")
            html_txt = "https://mariadb.com/" + a.get("href") if a else ""
            if len(html_name) and len(html_txt):
                if htmls_list is None:
                    htmls_list = {}  # 初始化为字典
                htmls_list[html_name] = html_txt
                with open(dir_filename, "a", encoding="utf-8") as w:
                    json.dump({html_name:html_txt}, w)
                    w.write('\n')
                print(html_name + ":" + html_txt)


def statements_htmls_crawler(Prefix):
    statements_htmls = {}
    merged_htmls_filename = "../../../FeatureKnowledgeBase/mariadb/SQL_Statements/SQL_Statements_HTMLs.json"
    for key, value in statements_category_htmls.items():
        statements_htmls[key] = {}
        print(key)
        dir_filename = Prefix + "SQL_Statements/SQL_Statements_HTMLs_" + key + ".jsonl"
        if os.path.exists(dir_filename):
            print("文件 " + dir_filename + " 已存在！")
            continue
        get_statements_htmls_category(dir_filename, key, value)

    if os.path.exists(merged_htmls_filename):
        print("文件 " + merged_htmls_filename + " 已存在！")
        return
    # 合并所有类别的htmls
    for key, value in statements_category_htmls.items():
        dir_filename = Prefix + "SQL_Statements/SQL_Statements_HTMLs_" + key + ".jsonl"
        with open(dir_filename, "r", encoding="utf-8") as r:
            lines = r.readlines()
        for line in lines:
            data = json.loads(line)
            statements_htmls[key].update(data)
    with open(merged_htmls_filename, "w", encoding="utf-8") as w:
        json.dump(statements_htmls, w, indent=4)

def htmls_crawler(html_start, html_end, dir_filename):
    if os.path.exists(dir_filename):
        print("文件 " + dir_filename + " 已存在！")
        return
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作

    htmls_table = {}  # 用于存储所有的htmls
    this_html = html_start  # 记录当下页面的html
    this_name = ""  # 当下页面的name
    next_html = ""  # 记录下一个页面的html
    next_name = ""  # 记录下一个页面的name

    # 要跳过的html
    skip_htmls = [
        "https://clickhouse.com/docs/en/sql-reference/functions/geo",
        "https://clickhouse.com/docs/en/sql-reference/aggregate-functions",
        "https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference",
        "https://clickhouse.com/docs/en/sql-reference/aggregate-functions/combinators",
        "https://clickhouse.com/docs/en/sql-reference/aggregate-functions/grouping_function",
        "https://clickhouse.com/docs/en/sql-reference/table-functions",
        "https://clickhouse.com/docs/en/sql-reference/window-functions",
        "https://clickhouse.com/docs/en/sql-reference/functions/udf",
        "https://clickhouse.com/docs/en/sql-reference/functions/in-functions",
        "https://clickhouse.com/docs/en/sql-reference/functions/machine-learning-functions",
        "https://clickhouse.com/docs/en/sql-reference/table-functions/deltalake"
    ]

    while True:
        # 不断读取当前页面中的下一个界面的html并存储到next_html中
        driver.get(this_html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
        WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
        soup = BeautifulSoup(driver.page_source, "html.parser")
        soup_next_html_a = soup.find("a", class_="pagination-nav__link pagination-nav__link--next paginationNavLink_UdUv")
        # next_html = "https://clickhouse.com" + soup_next_html_a.get("href") if soup_next_html_a else ""
        next_html = urljoin(this_html, soup_next_html_a.get("href")) if soup_next_html_a else ""
        soup_next_html_name = soup_next_html_a.find("div", class_="paginationNavLabel_YPzM pagination-nav__label") if soup_next_html_a else None
        next_name = soup_next_html_name.text if soup_next_html_name else ""

        # 将html加入到记录中
        if next_html not in skip_htmls:
            # 跳过部分html
            htmls_table[next_name] = next_html
            print(next_name + ":" + next_html)
        if next_html == html_end:
            # 到达最后一个html，跳出while循环
            break
        else:
            # 更新this_html，进入下一轮
            if next_name == "deltaLake":
                this_html = "https://clickhouse.com/docs/en/sql-reference/table-functions/dictionary"
            else:
                this_html = next_html
    return {"No Category": htmls_table}


