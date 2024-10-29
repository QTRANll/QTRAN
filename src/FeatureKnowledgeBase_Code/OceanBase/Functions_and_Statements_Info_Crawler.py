# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/18 09:77
# @Author  : zql
# @File    : Functions_and_Statements_Info_Crawler.py
# @Intro   : 获取OceanBase的Mysql模式和Oracle模式下，关于functions，operators和sql statements的详细信息

import json
import os
import time
from selenium import webdriver
from src.FeatureKnowledgeBase_Code.crawler_options import set_options
from bs4 import BeautifulSoup, Tag

prefix = "../../../Feature Knowledge Base/OceanBase/"


# 为所有的functions确认所属的categories，单个function可能属于多个category
def functions_categories(functions_htmls_filename, dir_filename):
    if os.path.exists(dir_filename):
        print("文件 " + dir_filename + " 已存在！")
        return
    with open(functions_htmls_filename, "r", encoding="utf-8") as rf:
        htmls = json.load(rf)

    title_categories = {}  # 存储所有title对应的categories
    for key_category, value_category in htmls.items():
        for key_title, value_html in value_category.items():
            if key_title not in title_categories:
                temp = {"Title": [key_title], "HTML": [value_html], "Category": []}
                title_categories[key_title] = temp
            title_categories[key_title]["Category"].append(key_category)

    with open(dir_filename, 'w', encoding='utf-8') as f:
        json.dump(title_categories, f, indent=4, ensure_ascii=False)


def is_text(tag_name, tag_text):
    if tag_name == 'style':
        #  跳过name = "style"
        return False
    elif tag_text == "":
        # 跳过空文本
        return False
    return True


def item_crawler(driver, result):
    driver.get(result["HTML"][0])  # 打开指定的URL:使用WebDriver打开指定的URL，加载页面内容
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    article_soup = soup.find("article", class_="typo-content")

    texts = []  # 存储处理的每一条文本内容
    subtitle_indexes = []  # 存储每个SubTitle在illustrations数组中的下标
    subtitles = []
    code_txt_indexes = []  # 存储每个code在数组中的下标
    for item in article_soup.children:
        # 跳过非Tag
        if isinstance(item, Tag) == 0:
            continue

        item_name = item.name
        item_class = item.get("class")
        item_text = item.text

        # 跳过非文本的Tag
        if is_text(item_name, item_text) is False:
            continue

        if item_name == 'h2':
            # 如果是SubTitle，则记录下标
            subtitle_indexes.append(len(texts))
            subtitles.append(item_text)
        elif item_name == 'div' and 'codeContainer' in item_class:
            # 如果是code，则记录下标
            code_txt_indexes.append(len(texts))
        elif item_name == "ul" or item_name == "ol":
            # 如果是列表
            li_sout = item.find_all("li")
            for li in li_sout:
                for li_item in li.children:
                    if li_item.text.strip() == "":
                        continue
                    elif li_item.name == 'div' and 'codeContainer' in li_item.get('class'):
                        # 如果是code，则记录下标
                        code_txt_indexes.append(len(texts))
                    texts.append(li_item.text)
            continue
        texts.append(item_text)

    # 遍历处理texts形成最终结果
    """
    * description：”描述“
    * feature：“声明”或“语法”或"语法声明"或”函数语法“或”语句“或”格式“
    * illustration：“说明”+”参数说明“+”参数解释“+”返回类型“
    * examples：“示例”
    """

    result_detailed = result
    if len(subtitle_indexes) == 0:
        # 没有SubTitle
        return result_detailed
    else:
        # 有SubTitle

        # 获取Feature：“声明”或“语法”或”语法声明“或”函数语法“或”语句“或格式
        feature_names = ["声明", "语法", "语法声明", "函数语法", "语句", "格式"]
        for name in feature_names:
            if name in subtitles:
                feature_start_index = texts.index(name)
                temp = subtitle_indexes.index(feature_start_index)
                features_end_index = subtitle_indexes[temp + 1]
                for code_index in code_txt_indexes:
                    if code_index in range(feature_start_index, features_end_index+1):
                        result_detailed["Feature"] += texts[code_index]
                break

        # 获取description：“描述”
        if '描述' in subtitles:
            description_start_index = texts.index('描述')
            temp = subtitle_indexes.index(description_start_index)
            if temp == len(subtitle_indexes)-1:
                result_detailed["Description"] = texts[description_start_index+1:]
            else:
                description_end_index = subtitle_indexes[temp+1]
                result_detailed["Description"] = texts[description_start_index+1:description_end_index]
        else:
            if subtitle_indexes[0] != 0:
                result_detailed["Description"] = texts[0:subtitle_indexes[0]]

        # 获取illustration：“说明”+”参数说明“+”参数解释“+”返回类型“
        if '说明' in subtitles:
            illustration_start_index = texts.index('说明')
            temp = subtitle_indexes.index(illustration_start_index)
            if temp == len(subtitle_indexes)-1:
                result_detailed["Illustration"] += texts[illustration_start_index+1:]
            else:
                illustration_end_index = subtitle_indexes[temp + 1]
                result_detailed["Illustration"] += texts[illustration_start_index+1:illustration_end_index]
        if '参数说明' in subtitles:
            illustration_start_index = texts.index('参数说明')
            temp = subtitle_indexes.index(illustration_start_index)
            if temp == len(subtitle_indexes)-1:
                result_detailed["Illustration"] += texts[illustration_start_index+1:]
            else:
                illustration_end_index = subtitle_indexes[temp + 1]
                result_detailed["Illustration"] += texts[illustration_start_index+1:illustration_end_index]
        if '参数解释' in subtitles:
            illustration_start_index = texts.index('参数解释')
            temp = subtitle_indexes.index(illustration_start_index)
            if temp == len(subtitle_indexes)-1:
                result_detailed["Illustration"] += texts[illustration_start_index+1:]
            else:
                illustration_end_index = subtitle_indexes[temp + 1]
                result_detailed["Illustration"] += texts[illustration_start_index+1:illustration_end_index]
        if '返回类型' in subtitles:
            illustration_start_index = texts.index('返回类型')
            temp = subtitle_indexes.index(illustration_start_index)
            if temp == len(subtitle_indexes)-1:
                result_detailed["Illustration"] += texts[illustration_start_index+1:]
            else:
                illustration_end_index = subtitle_indexes[temp + 1]
                result_detailed["Illustration"] += texts[illustration_start_index+1:illustration_end_index]

        # 获取detailed examples和examples：“示例”
        if '示例' in subtitles:
            examples_start_index = texts.index('示例')
            temp = subtitle_indexes.index(examples_start_index)
            if temp == len(subtitle_indexes)-1:
                examples_end_index = len(texts)-1
                result_detailed["Detailed Examples"] = texts[examples_start_index+1:]
            else:
                examples_end_index = subtitle_indexes[temp + 1]
                result_detailed["Detailed Examples"] = texts[examples_start_index+1:examples_end_index]
            # 添加code格式的examples
            examples_code = []
            for code_index in code_txt_indexes:
                print(texts[code_index])
                if code_index in range(examples_start_index, examples_end_index + 1):
                    examples_code.append(texts[code_index])
            result_detailed["Examples"] = examples_code

    return result_detailed


def information_crawler(initial_results_filename, results_dicname, exception_dicname, merged_results_filename, dropped_results_filename):
    options = set_options()
    driver = webdriver.Chrome(options=options)  # 创建一个Chrome浏览器的WebDriver对象，用于控制浏览器的操作

    # 打开并读取初步爬取结果，result
    with open(initial_results_filename, "r", encoding="utf-8") as rf:
        contents = json.load(rf)

    count = 0  # 记录信息爬取进度
    # 逐条爬取信息，并逐条存储到Results文件夹中
    for key_title, value in contents.items():
        if os.path.exists(results_dicname+"/"+key_title.replace('/', ' or ')+".json"):
            continue
        result = value
        result["Feature"] = ""
        result["Description"] = []
        result["Illustration"] = []
        result["Examples"] = []
        result["Detailed Examples"] = []

        final_result = {}
        exc_info = {}
        try:
            final_result[key_title] = item_crawler(driver, result)
            if os.path.exists(results_dicname + "/" + key_title.replace('/', ' or ') + ".json"):
                continue
            with open(results_dicname + "/" + key_title.replace('/', ' or ') + ".json", 'w',
                      encoding='utf-8') as f:
                json.dump(final_result, f, indent=4, ensure_ascii=False)
        except Exception as e:
            if os.path.exists(exception_dicname + "/" + key_title.replace('/', ' or ') + ".json"):
                continue
            exc_info[key_title] = str(e)
            with open(exception_dicname + "/" + key_title.replace('/', ' or ') + ".json", 'w',
                      encoding='utf-8') as f:
                json.dump(exc_info, f, indent=4, ensure_ascii=False)
        count = count + 1

        '''
        print(str(count)+"/"+str(len(contents)))
        print(key_title)
        print(result["HTML"][0])
        print('--------------')
        '''

    # 合并所有的数据
    if os.path.exists(merged_results_filename):
        print("文件 " + merged_results_filename + " 已存在！")
        return
    results_merged = {}
    results_dropped = {}
    filenames = os.listdir(results_dicname)
    # 合并Results文件夹中的所有信息，得到xxx_Results_merged.json文件,存储无效爬取信息的xxx_Results_dropped.json文件
    for filename in filenames:
        with open(results_dicname+"/"+filename, "r", encoding="utf-8") as rf:
            content = json.load(rf)
        for key, value in content.items():
            # 丢弃的无效爬取信息
            if value["Feature"] == "" or (len(value["Illustration"]) | len(value["Description"])) == 0:
                results_dropped[key] = value
                break
            results_merged[key] = value

    # 存储合并后的信息:merged,dropped
    with open(merged_results_filename, 'w', encoding='utf-8') as f:
        json.dump(results_merged, f, indent=4, ensure_ascii=False)
    with open(dropped_results_filename, 'w', encoding='utf-8') as f:
        json.dump(results_dropped, f, indent=4, ensure_ascii=False)
    print(len(results_merged))


# 将数据分类
def information_classify(htmls_category_filename, merged_results_filename, results_category_dicname):
    with open(htmls_category_filename, "r", encoding="utf-8") as rf:
        htmls = json.load(rf)

    with open(merged_results_filename, "r", encoding="utf-8") as rf:
        functions_merged = json.load(rf)

    for key_category, value_category in htmls.items():
        if os.path.exists(results_category_dicname+"/"+key_category.replace('/', ' or ') + ".json"):
            print("文件 " + results_category_dicname+"/"+key_category.replace('/', ' or ') + ".json" + " 已存在！")
            continue
        functions_temp = {}
        for key_title, value_html in value_category.items():
            if key_title in functions_merged:
                functions_temp[key_title] = functions_merged[key_title]
        with open(results_category_dicname+"/"+key_category.replace('/', ' or ')+".json", 'w', encoding='utf-8') as f:
            json.dump(functions_temp, f, indent=4, ensure_ascii=False)


def database_administration_statements():
    # database administration statements
    administration_statements_htmls_filename = prefix + "Database_Administration_Statements/Database_Administration_Statements_HTMLs_Category.json"
    administration_statements_dir_filename = prefix + "Database_Administration_Statements/Database_Administration_Statements_Results1.json"

    functions_categories(administration_statements_htmls_filename, administration_statements_dir_filename)

    database_administration_statements_crawler_params = [
        administration_statements_dir_filename,
        prefix + "Database_Administration_Statements/Database_Administration_Statements_Results",
        prefix + "Database_Administration_Statements/Database_Administration_Statements_Exceptions",
        prefix + "Database_Administration_Statements/Database_Administration_Statements_Results_merged.json",
        prefix + "Database_Administration_Statements/Database_Administration_Statements_Results_dropped.json",
    ]

    information_crawler(database_administration_statements_crawler_params[0],
                        database_administration_statements_crawler_params[1],
                        database_administration_statements_crawler_params[2],
                        database_administration_statements_crawler_params[3],
                        database_administration_statements_crawler_params[4])

    database_administration_statements_classify_params = [
        prefix + "Database_Administration_Statements/Database_Administration_Statements_HTMLs_Category.json",
        prefix + "Database_Administration_Statements/Database_Administration_Statements_Results_merged.json",
        prefix + "Database_Administration_Statements/Database_Administration_Statements_Results_Category"
    ]

    information_classify(database_administration_statements_classify_params[0],
                         database_administration_statements_classify_params[1],
                         database_administration_statements_classify_params[2])
    print('--------------------------------------------')

def functions_mysql():
    # functions_mysql
    functions_mysql_htmls_filename = prefix + "Functions_MySQL/Functions_MySQL_HTMLs_Category.json"
    functions_mysql_dir_filename = prefix + "Functions_MySQL/Functions_Mysql_Results1.json"

    functions_categories(functions_mysql_htmls_filename, functions_mysql_dir_filename)

    functions_mysql_crawler_params = [
        functions_mysql_dir_filename,
        prefix + "Functions_Mysql/Functions_Mysql_Results",
        prefix + "Functions_Mysql/Functions_Mysql_Exceptions",
        prefix + "Functions_Mysql/Functions_Mysql_Results_merged.json",
        prefix + "Functions_Mysql/Functions_Mysql_Results_dropped.json",
    ]

    information_crawler(functions_mysql_crawler_params[0], functions_mysql_crawler_params[1],
                        functions_mysql_crawler_params[2], functions_mysql_crawler_params[3],
                        functions_mysql_crawler_params[4])

    functions_mysql_classify_params = [
        prefix + "Functions_Mysql/Functions_Mysql_HTMLs_Category.json",
        prefix + "Functions_Mysql/Functions_Mysql_Results_merged.json",
        prefix + "Functions_Mysql/Functions_Mysql_Results_Category"
    ]

    information_classify(functions_mysql_classify_params[0], functions_mysql_classify_params[1],
                         functions_mysql_classify_params[2])
    print('--------------------------------------------')


def functions_oracle():
    # functions_oracle
    functions_oracle_htmls_filename = prefix + "Functions_Oracle/Functions_Oracle_HTMLs_Category.json"
    functions_oracle_dir_filename = prefix + "Functions_Oracle/Functions_Oracle_Results1.json"

    functions_categories(functions_oracle_htmls_filename, functions_oracle_dir_filename)

    functions_oracle_crawler_params = [
        functions_oracle_dir_filename,
        prefix + "Functions_Oracle/Functions_Oracle_Results",
        prefix + "Functions_Oracle/Functions_Oracle_Exceptions",
        prefix + "Functions_Oracle/Functions_Oracle_Results_merged.json",
        prefix + "Functions_Oracle/Functions_Oracle_Results_dropped.json",
    ]

    information_crawler(functions_oracle_crawler_params[0], functions_oracle_crawler_params[1], functions_oracle_crawler_params[2], functions_oracle_crawler_params[3], functions_oracle_crawler_params[4])

    functions_oracle_classify_params = [
        prefix + "Functions_Oracle/Functions_Oracle_HTMLs_Category.json",
        prefix + "Functions_Oracle/Functions_Oracle_Results_merged.json",
        prefix + "Functions_Oracle/Functions_Oracle_Results_Category"
    ]

    information_classify(functions_oracle_classify_params[0], functions_oracle_classify_params[1],
                         functions_oracle_classify_params[2])
    print('--------------------------------------------')


def statements_mysql():
    # statements_mysql
    statements_mysql_htmls_filename = prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_HTMLs_Category.json"
    statements_mysql_dir_filename = prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_Results1.json"

    functions_categories(statements_mysql_htmls_filename, statements_mysql_dir_filename)

    statements_mysql_crawler_params = [
        statements_mysql_dir_filename,
        prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_Results",
        prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_Exceptions",
        prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_Results_merged.json",
        prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_Results_dropped.json",
    ]

    information_crawler(statements_mysql_crawler_params[0],
                        statements_mysql_crawler_params[1],
                        statements_mysql_crawler_params[2],
                        statements_mysql_crawler_params[3],
                        statements_mysql_crawler_params[4])

    statements_mysql_classify_params = [
        prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_HTMLs_Category.json",
        prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_Results_merged.json",
        prefix + "SQL_Statements_MySQL/SQL_Statements_MySQL_Results_Category"
    ]

    information_classify(statements_mysql_classify_params[0],
                         statements_mysql_classify_params[1],
                         statements_mysql_classify_params[2])
    print('--------------------------------------------')


def statements_oracle():
    # statements_oracle
    statements_oracle_htmls_filename = prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_HTMLs_Category.json"
    statements_oracle_dir_filename = prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_Results1.json"

    functions_categories(statements_oracle_htmls_filename, statements_oracle_dir_filename)

    statements_oracle_crawler_params = [
        statements_oracle_dir_filename,
        prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_Results",
        prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_Exceptions",
        prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_Results_merged.json",
        prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_Results_dropped.json",
    ]

    information_crawler(statements_oracle_crawler_params[0],
                        statements_oracle_crawler_params[1],
                        statements_oracle_crawler_params[2],
                        statements_oracle_crawler_params[3],
                        statements_oracle_crawler_params[4])

    statements_oracle_classify_params = [
        prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_HTMLs_Category.json",
        prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_Results_merged.json",
        prefix + "SQL_Statements_Oracle/SQL_Statements_Oracle_Results_Category"
    ]

    information_classify(statements_oracle_classify_params[0],
                         statements_oracle_classify_params[1],
                         statements_oracle_classify_params[2])
    print('--------------------------------------------')


database_administration_statements()
functions_mysql()
functions_oracle()
statements_mysql()
statements_oracle()
