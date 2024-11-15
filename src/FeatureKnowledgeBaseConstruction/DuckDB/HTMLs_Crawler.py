from src.Tools.crawler_options import set_options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin
def htmls_crawler(html):
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
        href = urljoin(html, soup_li.find("a").get("href"))
        if href in skip_htmls:
            continue
        htmls_table[name] = href
    return {"No Category": htmls_table}
