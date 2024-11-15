import os
import json
from src.FeatureKnowledgeBaseConstruction.MariaDB.HTMLs_Crawler import ops_htmls_crawler, funcs_htmls_crawler
from src.FeatureKnowledgeBaseConstruction.MariaDB.Info_Crawler import crawler_results, preprocess_results
from src.Tools.crawler_options import category_classifier
def mariadb_crawler():
    dic_path = os.path.join(os.getcwd(),"..", "..", "..", "Feature Knowledge Base", "MariaDB")
    feature_types = ["DataTypes", "Functions", "Operators"]
    sub_dic = ["Results", "Results_Category"]
    htmls_list = {
        "Functions": "https://mariadb.com/kb/en/function-and-operator-reference/",
        "Operators": "https://mariadb.com/kb/en/operators/",
        "DataTypes": "https://mariadb.com/kb/en/data-types/"
    }

    for feature in feature_types:
        # make dictionaries
        feature_dic = os.path.join(dic_path, feature)
        if not os.path.exists(feature_dic):
            os.makedirs(feature_dic)
        for sub in sub_dic:
            sub_dic_path = os.path.join(feature_dic, sub)
            if not os.path.exists(sub_dic_path):
                os.makedirs(sub_dic_path)

    # htmls crawler
    op_html_path = os.path.join(dic_path, "Operators", "HTMLs.json")
    if os.path.exists(op_html_path):
        print("File " + op_html_path + " exists！")
    else:
        op_htmls = ops_htmls_crawler(htmls_list["Operators"])
        with open(op_html_path, 'w', encoding='utf-8') as f:
            json.dump(op_htmls, f, indent=4)

    func_op_html_path = os.path.join(dic_path, "Functions", "HTMLs.json")
    if os.path.exists(func_op_html_path):
        print("File " + func_op_html_path + " exists！")
    else:
        func_op_htmls = funcs_htmls_crawler(htmls_list["Functions"], op_html_path, func_op_html_path)
        with open(func_op_html_path, 'w', encoding='utf-8') as f:
            json.dump(func_op_htmls, f, indent=4)


    data_html_path = os.path.join(dic_path, "DataTypes", "HTMLs.json")
    if os.path.exists(data_html_path):
        print("File " + data_html_path + " exists！")
    else:
        data_htmls = ops_htmls_crawler(htmls_list["DataTypes"])
        with open(data_html_path, 'w', encoding='utf-8') as f:
            json.dump(data_htmls, f, indent=4)

    # information crawler and classification
    # functions and operators
    op_results_dic = os.path.join(dic_path, "Operators", "Results")
    op_results_category_dic = os.path.join(dic_path, "Operators", "Results_Category")
    crawler_results("Operators", op_html_path, op_results_dic)
    category_classifier(op_results_dic,op_results_category_dic)

    func_results_dic = os.path.join(dic_path, "Functions", "Results")
    func_results_category_dic = os.path.join(dic_path, "Functions", "Results_Category")
    crawler_results("Functions", func_op_html_path, func_results_dic)
    preprocess_results(func_results_dic)
    category_classifier(func_results_dic, func_results_category_dic)


    # data types
    htmls_filename = os.path.join(dic_path, "DataTypes", "HTMLs.json")
    data_results_dic = os.path.join(dic_path, "DataTypes", "Results")
    data_results_category_dic = os.path.join(dic_path, "DataTypes", "Results_Category")
    crawler_results("DataTypes", htmls_filename, data_results_dic)
    category_classifier(data_results_dic, data_results_category_dic)


mariadb_crawler()
