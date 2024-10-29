# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/16 14:47
# @Author  : zql
# @File    : HTMLs_Crawler_MySQL.py
# @Intro   : 获取OceanBase的Mysql模式和Oracle模式下，关于functions，operators和sql statements的所有htmls


import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from src.FeatureKnowledgeBase_Code.crawler_options import set_options


def htmls_crawler(html_start, title_end, dir_txt):
    if os.path.exists(dir_txt):
        print("文件 " + dir_txt + " 已存在！")
        return
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作

    htmls_administration = {}

    # 重复直到遇到下一个页面名称为“数据类型概述”时停止，说明到下一个单元了
    while True:
        driver.get(html_start)  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
        time.sleep(2.5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        div_footer_soup = soup.find("div", class_="footer___2zbSv")

        # 从第一个“管理命令概述”页面开始，在右下角的“下一篇”按钮处获取下一个页面的标题及html
        if div_footer_soup:
            div_next_soup = div_footer_soup.find("div", class_="next___15dlz")
            # 获取下一个页面的名称
            title_soup = div_next_soup.find("span", class_="title___1j4ib")
            title_temp = title_soup.text
            # 获取下一个页面的html
            a_soup = div_next_soup.find("a", class_="item___rfjeA")
            html_temp = "https://www.oceanbase.com" + a_soup.get("href")

            print(title_temp+":"+html_temp)
            htmls_administration[title_temp] = html_temp
            html_start = html_temp   # 更新为下一个html
            with open(dir_txt, 'a', encoding='utf-8') as f:
                f.write(title_temp+":"+html_temp+'\n')

            if title_end in title_temp:
                break


dir_prefix = "../../../Feature Knowledge Base/OceanBase/"
# Database Administration Statements
html_start_admin = "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000000820805"
title_end_admin = "SET ENCRYPTION"
dir_txt_admin = dir_prefix + "Database_Administration_Statements/Database_Administration_Statements_HTMLs.txt"

# Functions (MySQL模式)
html_start_func_mysql = "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000000822091"
title_end_fun_mysql = "VALUES"
dir_txt_func_mysql = dir_prefix + "Functions_MySQL/Functions_MySQL_HTMLs.txt"

# Functions (Oracle模式)
html_start_func_oracle = "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000000821936"
title_end_fun_oracle = "OB_TRANSACTION_ID"
dir_txt_func_oracle = dir_prefix + "Functions_Oracle/Functions_Oracle_HTMLs.txt"

# SQL Statements (MySQL模式)
html_start_state_mysql = "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000001053491"
title_end_state_mysql = "VALUES"
dir_txt_state_mysql = dir_prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_HTMLs.txt"

# SQL Statements (MyOracle模式)
html_start_state_oracle = "https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000001053406"
title_end_state_oracle = "TRANSACTION"
dir_txt_state_oracle = dir_prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_HTMLs.txt"


htmls_crawler(html_start_admin, title_end_admin, dir_txt_admin)

htmls_crawler(html_start_func_mysql, title_end_fun_mysql, dir_txt_func_mysql)
htmls_crawler(html_start_func_oracle, title_end_fun_oracle, dir_txt_func_oracle)

htmls_crawler(html_start_state_mysql, title_end_state_mysql, dir_txt_state_mysql)
htmls_crawler(html_start_state_oracle, title_end_state_oracle, dir_txt_state_oracle)
