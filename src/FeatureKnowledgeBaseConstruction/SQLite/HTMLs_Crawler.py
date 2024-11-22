from src.Tools.Crawler.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

def funcs_htmls_crawler(html):
    results_list = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_show_hide = soup.find("ul", class_="showhide")
    for li_item in soup_show_hide.children:
        #  跳过非Tag
        if isinstance(li_item, Tag) == 0:
            continue
        soup_a = li_item.find("a")
        title_name = soup_a.text
        soup_a_list = li_item.find_all("a", class_="sh_link")
        for a_item in soup_a_list:
            subtitle = a_item.text
            html_temp = urljoin(html, a_item.get("href"))
            if "function" in subtitle:
                results_list[subtitle] = html_temp

    results_list["Built-In Mathematical SQL function"] = "https://sqlite.org/lang_mathfunc.html"
    return {"No Category": results_list}


def datatypes_htmls_crawler(html):
    results_list = {}
    timeout = 5  # 等待时间
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作
    driver.get(html)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    WebDriverWait(driver, timeout)  # 创建一个WebDriverWait对象，设置最大等待时间为50秒，用于等待页面加载完成
    soup = BeautifulSoup(driver.page_source, "html.parser")
    soup_show_hide = soup.find("ul", class_="showhide")
    for li_item in soup_show_hide.children:
        #  跳过非Tag
        if isinstance(li_item, Tag) == 0:
            continue
        soup_a = li_item.find("a")
        title_name = soup_a.text
        soup_a_list = li_item.find_all("a", class_="sh_link")
        for a_item in soup_a_list:
            subtitle = a_item.text
            html_temp = urljoin(html, a_item.get("href"))
            if "datatype" == subtitle:
                results_list[subtitle] = html_temp
    return {"No Category": results_list}