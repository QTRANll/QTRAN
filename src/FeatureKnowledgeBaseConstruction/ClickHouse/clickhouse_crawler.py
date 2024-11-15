import os
import json
from src.FeatureKnowledgeBaseConstruction.ClickHouse.HTMLs_Crawler import htmls_crawler
from src.FeatureKnowledgeBaseConstruction.ClickHouse.Info_Crawler import crawler_results
from src.Tools.crawler_options import category_classifier
def clickhouse_crawler():
    dic_path = os.path.join(os.getcwd(),"..", "..", "..", "Feature Knowledge Base", "Clickhouse")
    feature_types = ["DataTypes", "Functions", "Operators"]
    sub_dic = ["Results", "Results_Category"]
    htmls_start_list = {
        "Functions": "https://clickhouse.com/docs/en/sql-reference/functions",
        "Operators": "https://clickhouse.com/docs/en/sql-reference/window-functions/leadInFrame",
        "DataTypes": "https://clickhouse.com/docs/en/sql-reference/data-types"
    }
    htmls_end_list = {
        "Functions": "https://clickhouse.com/docs/en/sql-reference/window-functions/leadInFrame",
        "Operators": "https://clickhouse.com/docs/en/sql-reference/operators/exists",
        "DataTypes": "https://clickhouse.com/docs/en/sql-reference/data-types/newjson"
    }
    # htmls crawler
    for feature in feature_types:
        # make dictionaries
        feature_dic = os.path.join(dic_path, feature)
        if not os.path.exists(feature_dic):
            os.makedirs(feature_dic)
        for sub in sub_dic:
            sub_dic_path = os.path.join(feature_dic, sub)
            if not os.path.exists(sub_dic_path):
                os.makedirs(sub_dic_path)
        # crawl the htmls list
        html_path = os.path.join(feature_dic, "HTMLs.json")
        if os.path.exists(html_path):
            print("File " + html_path + " exists！")
            continue
        htmls = htmls_crawler(htmls_start_list[feature], htmls_end_list[feature], html_path)
        with open(html_path, 'w', encoding='utf-8') as f:
            json.dump(htmls, f, indent=4)

    # functions and operators information crawler and classification
    for feature in feature_types:
        htmls_filename = os.path.join(dic_path, feature, "HTMLs.json")
        results_dic = os.path.join(dic_path, feature, "Results")
        results_category_dic = os.path.join(dic_path, feature, "Results_Category")
        crawler_results(feature, htmls_filename, results_dic)
        category_classifier(results_dic, results_category_dic)

clickhouse_crawler()