import json
import os
from src.FeatureKnowledgeBase_Code.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


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
    merged_htmls_filename = "../../../Feature Knowledge Base/MariaDB/SQL_Statements/SQL_Statements_HTMLs.json"
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




# 爬取Functions and Operators页面内的Reference Table的所有表格项并存储
def funcs_htmls_crawler(html_func_op, dir_filename_fun_op):
    with open(prefix + "Operators/Operators_HTMLs_List.json", 'r', encoding='utf-8') as r:
        ops_htmls = json.load(r)

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
                html = "https://mariadb.com/" + soup_table_td_selected.find("a").get("href") if soup_table_td_selected.find("a") else ""
                if html in ops_htmls:
                    continue
                else:
                    reference_table[soup_table_td_selected.text] = html
    with open(dir_filename_fun_op, 'w', encoding='utf-8') as f:
        json.dump({"No Category":reference_table}, f, indent=4)



def ops_htmls_crawler(html, dir_filename):
    ops_list = {}
    ops_htmls = []
    if len(html) == 0:
        return
    if os.path.exists(dir_filename):
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
    soup_h3s = soup_section.find_all("h3")[:-1]
    soup_uls = soup_section.find_all("ul", class_="media-list listing embedded")
    for index in range(len(soup_h3s)):
        list_temp = {}
        soup_h3 = soup_h3s[index]
        soup_ul = soup_uls[index]
        op_category = soup_h3.text.strip()
        # 处理ul内所有链接
        for soup_li in soup_ul.children:
            soup_a = soup_li.find("a")
            soup_h4 = soup_li.find("h4")
            if soup_a == -1:
                continue
            title = soup_h4.text.strip()
            html = "https://mariadb.com/" + soup_a.get("href")
            list_temp[title] = html
            ops_htmls.append(html)
        ops_list[op_category] = list_temp
        print("---------")

    with open(dir_filename, 'w', encoding='utf-8') as f:
        json.dump(ops_list, f, indent=4)
    with open(prefix + "Operators/Operators_HTMLs_List.json", 'w', encoding='utf-8') as f:
        json.dump(ops_htmls, f, indent=4)

prefix = "../../../Feature Knowledge Base/MariaDB/"
# statements_htmls_crawler(prefix)


html_op = "https://mariadb.com/kb/en/operators/"
dir_filename_op = prefix + "Operators/Operators_HTMLs.json"  # functions 和 operators的目录页
# ops_htmls_crawler(html_op, dir_filename_op)


html_func_op = "https://mariadb.com/kb/en/function-and-operator-reference/"
dir_filename_fun_op = prefix + "Functions/Functions_HTMLs.json"  # functions 和 operators的目录页
# funcs_htmls_crawler(html_func_op, dir_filename_fun_op)
