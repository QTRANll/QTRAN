import os
import json
from src.FeatureKnowledgeBaseConstruction.MySQL.HTMLs_Crawler import htmls_crawler
from src.FeatureKnowledgeBaseConstruction.MySQL.Reference_Table_Crawler import reference_tables_crawler
from src.FeatureKnowledgeBaseConstruction.MySQL.Info_Crawler import functions_and_operators_table_crawler, data_types_crawler
from src.Tools.Crawler.crawler_options import category_classifier
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

def mysql_crawler():
    dic_path = os.path.join(current_dir,"..", "..", "..", "FeatureKnowledgeBase", "mysql")
    feature_types = ["datatype", "function", "operator"]
    sub_dic = ["results", "results_category"]
    htmls_list = {
        "function": "https://dev.mysql.com/doc/refman/8.0/en/functions.html",
        "operator": "https://dev.mysql.com/doc/refman/8.0/en/functions.html",
        "datatype": "https://dev.mysql.com/doc/refman/8.0/en/data-types.html"
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

    # reference tables Crawler
    for feature in feature_types:
        # functions + operators
        if feature in ["function", "operator"]:
            feature_dic = os.path.join(dic_path, feature)
            html_path = os.path.join(feature_dic, "HTMLs.json")
            reference_table_results_path = os.path.join(dic_path, "reference_table_results")
            if not os.path.exists(reference_table_results_path):
                os.makedirs(reference_table_results_path)
            reference_tables_crawler(html_path, reference_table_results_path)
            # Remove duplicates
            function_references_merged = []
            operator_references_merged = []
            reference_htmls = []
            files = os.listdir(reference_table_results_path)
            for file in files:
                with open(os.path.join(reference_table_results_path, file), "r", encoding="utf-8") as r:
                    contents = json.load(r)
                for content in contents:
                    if content["Reference HTML"] not in reference_htmls:
                        reference_htmls.append(content["Reference HTML"])
                        content["Category"] = [content["Category"] ]
                        if "(" in content["Name"] and ")" in content["Name"]:
                            function_references_merged.append(content)
                        else:
                            operator_references_merged.append(content)
                    else:
                        for item in function_references_merged:
                            if item["Reference HTML"] == content["Reference HTML"]:
                                if content["Category"] not in item["Category"] and len(content["Category"]):
                                    item["Category"].append(content["Category"])
                        for item in operator_references_merged:
                            if item["Reference HTML"] == content["Reference HTML"]:
                                if content["Category"] not in item["Category"] and len(content["Category"]):
                                    item["Category"].append(content["Category"])
            with open(os.path.join(dic_path, "functions_reference_table_results_merged.json"), "w", encoding="utf-8") as w:
                json.dump(function_references_merged, w, indent=4)
            with open(os.path.join(dic_path, "operators_reference_table_results_merged.json"), "w", encoding="utf-8") as w:
                json.dump(operator_references_merged, w, indent=4)

    # functions and operators information Crawler
    functions_reference_table = os.path.join(dic_path, "functions_reference_table_results_merged.json")
    operators_reference_table = os.path.join(dic_path, "operators_reference_table_results_merged.json")
    functions_results = os.path.join(dic_path, "function", "results")
    operators_results = os.path.join(dic_path, "operator", "results")
    functions_category = os.path.join(dic_path, "function", "results_category")
    operators_category = os.path.join(dic_path, "operator", "results_category")
    functions_and_operators_table_crawler(functions_reference_table, functions_results)
    functions_and_operators_table_crawler(operators_reference_table, operators_results)
    # data types information Crawler
    feature_dic = os.path.join(dic_path, "datatype")
    data_types_htmls = os.path.join(feature_dic, "HTMLs.json")
    data_types_results = os.path.join(dic_path, "datatype", "results")
    data_types_category = os.path.join(dic_path, "datatype", "results_category")
    data_types_crawler(data_types_htmls, data_types_results)

    # category
    category_classifier(functions_results, functions_category)
    category_classifier(operators_results, operators_category)
    category_classifier(data_types_results, data_types_category)
