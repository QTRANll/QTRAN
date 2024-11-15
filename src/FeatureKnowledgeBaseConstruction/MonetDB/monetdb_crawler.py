import os
import json
from src.FeatureKnowledgeBaseConstruction.MonetDB.HTMLs_Crawler import htmls_crawler
from src.FeatureKnowledgeBaseConstruction.MonetDB.Info_Crawler import crawler_results
from src.Tools.crawler_options import category_classifier
def monetdb_crawler():
    dic_path = os.path.join(os.getcwd(),"..", "..", "..", "Feature Knowledge Base", "MonetDB")
    feature_types = ["DataTypes", "Functions", "Operators"]
    sub_dic = ["Results", "Results_Category"]
    htmls_list = {
        "Functions": "https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/",
        "Operators": "https://www.monetdb.org/documentation-Aug2024/user-guide/sql-functions/",
        "DataTypes": "https://www.monetdb.org/documentation-Aug2024/user-guide/sql-manual/data-types/"
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
        htmls = htmls_crawler(htmls_list[feature])
        with open(html_path, 'w', encoding='utf-8') as f:
            json.dump(htmls, f, indent=4)


    # information crawler and classification
    # functions and operators
    htmls_filename = os.path.join(dic_path, "Functions", "HTMLs.json")
    func_results_dic = os.path.join(dic_path, "Functions", "Results")
    func_results_category_dic = os.path.join(dic_path, "Functions", "Results_Category")
    op_results_dic = os.path.join(dic_path, "Operators", "Results")
    op_results_category_dic = os.path.join(dic_path, "Operators", "Results_Category")
    crawler_results("Functions", htmls_filename, func_results_dic, op_results_dic)
    category_classifier(func_results_dic, func_results_category_dic)
    category_classifier(op_results_dic, op_results_category_dic)

    # data types
    htmls_filename = os.path.join(dic_path, "DataTypes", "HTMLs.json")
    data_results_dic = os.path.join(dic_path, "DataTypes", "Results")
    data_results_category_dic = os.path.join(dic_path, "DataTypes", "Results_Category")
    crawler_results("DataTypes", htmls_filename, data_results_dic, "")
    category_classifier(data_results_dic, data_results_category_dic)

monetdb_crawler()