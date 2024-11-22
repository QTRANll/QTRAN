from src.Tools.Crawler.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def ops_htmls_crawler(html):
    operators_list = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 查找到页面内所有的table
    soup_tables = soup.find_all("table")
    # 分别处理四个table
    for index in range(len(soup_tables)):
        soup_table = soup_tables[index]
        soup_body = soup_table.find("tbody") if soup_table else None
        soup_trs = soup_body.find_all("tr")
        # 遍历table内所有tr
        for soup_tr in soup_trs:
            soup_td_first = soup_tr.find("td")
            name = soup_td_first.text
            html_temp = soup_td_first.find("a").get("href")
            if name not in operators_list:
                operators_list[name] = html_temp
    return {"No Category": operators_list}


def funcs_htmls_crawler(html, html_start, html_end):
    results_list = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_a_items = soup.find_all("a")
    start_flag = False
    for a_item in soup_a_items:
        a_name = a_item.text
        a_html = urljoin(html, a_item.get("href"))
        if a_html == html_start:
            start_flag = True
        if a_html == html_end:
            break
        if start_flag and ("-functions" in a_html or "data-type" in a_html):
            print(a_name + ":" + a_html)
            results_list[a_name] = a_html
    return {"No Category": results_list}


