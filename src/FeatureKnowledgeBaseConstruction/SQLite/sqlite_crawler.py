import os
import json
from src.FeatureKnowledgeBaseConstruction.SQLite.HTMLs_Crawler import funcs_htmls_crawler, datatypes_htmls_crawler
from src.FeatureKnowledgeBaseConstruction.SQLite.Info_Crawler import crawler_results
from src.Tools.crawler_options import category_classifier

def sqlite_crawler():
    dic_path = os.path.join(os.getcwd(),"..", "..", "..", "Feature Knowledge Base", "Sqlite")
    feature_types = ["Functions", "DataTypes", "Operators"]
    sub_dic = ["Results", "Results_Category"]
    htmls_list = {
        "Functions": "https://sqlite.org/docs.html",
        "DataTypes": "https://sqlite.org/docs.html"
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
    func_html_path = os.path.join(dic_path, "Functions", "HTMLs.json")
    if os.path.exists(func_html_path):
        print("File " + func_html_path + " exists！")
    else:
        func_op_htmls = funcs_htmls_crawler(htmls_list["Functions"])
        with open(func_html_path, 'w', encoding='utf-8') as f:
            json.dump(func_op_htmls, f, indent=4, ensure_ascii=False)

    data_html_path = os.path.join(dic_path, "DataTypes", "HTMLs.json")
    if os.path.exists(data_html_path):
        print("File " + data_html_path + " exists！")
    else:
        data_htmls = datatypes_htmls_crawler(htmls_list["DataTypes"])
        with open(data_html_path, 'w', encoding='utf-8') as f:
            json.dump(data_htmls, f, indent=4, ensure_ascii=False)

    # information crawler and classification
    feature_types = ["Functions", "Operators", "DataTypes"]
    for feature in feature_types:
        htmls_filename = os.path.join(dic_path, feature, "HTMLs.json")
        results_dic = os.path.join(dic_path, feature, "Results")
        results_category_dic = os.path.join(dic_path, feature, "Results_Category")
        crawler_results(feature, htmls_filename, results_dic)
        category_classifier(results_dic, results_category_dic)

sqlite_crawler()
