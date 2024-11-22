import os
import json
from src.FeatureKnowledgeBaseConstruction.MariaDB.HTMLs_Crawler import ops_htmls_crawler, funcs_htmls_crawler
from src.FeatureKnowledgeBaseConstruction.MariaDB.Info_Crawler import crawler_results, preprocess_results
from src.Tools.Crawler.crawler_options import category_classifier
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

def mariadb_crawler():
    dic_path = os.path.join(current_dir,"..", "..", "..", "FeatureKnowledgeBase", "mariadb")
    feature_types = ["datatype", "function", "operator"]
    sub_dic = ["results", "results_category"]
    htmls_list = {
        "function": "https://mariadb.com/kb/en/function-and-operator-reference/",
        "operator": "https://mariadb.com/kb/en/operators/",
        "datatype": "https://mariadb.com/kb/en/data-types/"
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

    # htmls Crawler
    op_html_path = os.path.join(dic_path, "operator", "HTMLs.json")
    if os.path.exists(op_html_path):
        print("File " + op_html_path + " exists！")
    else:
        op_htmls = ops_htmls_crawler(htmls_list["operator"])
        with open(op_html_path, 'w', encoding='utf-8') as f:
            json.dump(op_htmls, f, indent=4)

    func_op_html_path = os.path.join(dic_path, "function", "HTMLs.json")
    if os.path.exists(func_op_html_path):
        print("File " + func_op_html_path + " exists！")
    else:
        func_op_htmls = funcs_htmls_crawler(htmls_list["function"], op_html_path, func_op_html_path)
        with open(func_op_html_path, 'w', encoding='utf-8') as f:
            json.dump(func_op_htmls, f, indent=4)


    data_html_path = os.path.join(dic_path, "datatype", "HTMLs.json")
    if os.path.exists(data_html_path):
        print("File " + data_html_path + " exists！")
    else:
        data_htmls = ops_htmls_crawler(htmls_list["datatype"])
        with open(data_html_path, 'w', encoding='utf-8') as f:
            json.dump(data_htmls, f, indent=4)

    # information Crawler and classification
    # functions and operators
    op_results_dic = os.path.join(dic_path, "operator", "results")
    op_results_category_dic = os.path.join(dic_path, "operator", "results_category")
    crawler_results("operator", op_html_path, op_results_dic)
    category_classifier(op_results_dic,op_results_category_dic)

    func_results_dic = os.path.join(dic_path, "function", "results")
    func_results_category_dic = os.path.join(dic_path, "function", "results_category")
    crawler_results("function", func_op_html_path, func_results_dic)
    preprocess_results(func_results_dic)
    category_classifier(func_results_dic, func_results_category_dic)


    # data types
    htmls_filename = os.path.join(dic_path, "datatype", "HTMLs.json")
    data_results_dic = os.path.join(dic_path, "datatype", "results")
    data_results_category_dic = os.path.join(dic_path, "datatype", "results_category")
    crawler_results("datatype", htmls_filename, data_results_dic)
    category_classifier(data_results_dic, data_results_category_dic)
