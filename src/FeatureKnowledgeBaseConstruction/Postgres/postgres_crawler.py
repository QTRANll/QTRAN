import os
import json
from src.FeatureKnowledgeBaseConstruction.Postgres.HTMLs_Crawler import htmls_crawler
from src.FeatureKnowledgeBaseConstruction.Postgres.Info_Crawler import crawler_results
from src.Tools.Crawler.crawler_options import category_classifier
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

def postgres_crawler():
    dic_path = os.path.join(current_dir,"..", "..", "..", "FeatureKnowledgeBase", "postgres")
    feature_types = ["datatype", "function", "operator"]
    sub_dic = ["results", "results_category"]
    htmls_list = {
        "function": "https://www.postgresql.org/docs/16/functions.html",
        "operator": "https://www.postgresql.org/docs/16/functions.html",
        "datatype": "https://www.postgresql.org/docs/16/datatype.html"
    }
    # htmls Crawler
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
        htmls = htmls_crawler(htmls_list[feature])

        with open(html_path, 'w', encoding='utf-8') as f:
            json.dump(htmls, f, indent=4)

    # information Crawler and classification
    # functions and operators
    htmls_filename = os.path.join(dic_path, "function", "HTMLs.json")
    func_results_dic = os.path.join(dic_path, "function", "results")
    func_results_category_dic = os.path.join(dic_path, "function", "results_category")
    op_results_dic = os.path.join(dic_path, "operator", "results")
    op_results_category_dic = os.path.join(dic_path, "operator", "results_category")
    crawler_results("function", htmls_filename, func_results_dic, op_results_dic)
    category_classifier(func_results_dic, func_results_category_dic)
    category_classifier(op_results_dic, op_results_category_dic)

    # data types
    htmls_filename = os.path.join(dic_path, "datatype", "HTMLs.json")
    data_results_dic = os.path.join(dic_path, "datatype", "results")
    data_results_category_dic = os.path.join(dic_path, "datatype", "results_category")
    crawler_results("datatype", htmls_filename, data_results_dic, "")
    category_classifier(data_results_dic, data_results_category_dic)