import os
import json
from src.FeatureKnowledgeBaseConstruction.TiDB.HTMLs_Crawler import ops_htmls_crawler, funcs_htmls_crawler
from src.FeatureKnowledgeBaseConstruction.TiDB.Info_Crawler import crawler_results
from src.Tools.crawler_options import category_classifier
def tidb_crawler():
    dic_path = os.path.join(os.getcwd(),"..", "..", "..", "Feature Knowledge Base", "TiDB")
    feature_types = ["DataTypes", "Functions", "Operators"]
    sub_dic = ["Results", "Results_Category"]
    htmls_list = {
        "Functions": "https://docs.pingcap.com/zh/tidb/v8.3/json-functions-create",
        "Functions_start": "https://docs.pingcap.com/zh/tidb/v8.3/control-flow-functions",
        "Functions_end": "https://docs.pingcap.com/zh/tidb/v8.3/oracle-functions-to-tidb",
        "Operators": "https://docs.pingcap.com/zh/tidb/v8.3/operators",
        "DataTypes": "https://docs.pingcap.com/zh/tidb/v8.3/data-type-numeric",
        "DataTypes_start": "https://docs.pingcap.com/zh/tidb/v8.3/data-type-numeric",
        "DataTypes_end": "https://docs.pingcap.com/zh/tidb/v8.3/clustered-indexes"
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
            json.dump(op_htmls, f, indent=4, ensure_ascii=False)

    func_html_path = os.path.join(dic_path, "Functions", "HTMLs.json")
    if os.path.exists(func_html_path):
        print("File " + func_html_path + " exists！")
    else:
        func_op_htmls = funcs_htmls_crawler(htmls_list["Functions"],htmls_list["Functions_start"], htmls_list["Functions_end"])
        with open(func_html_path, 'w', encoding='utf-8') as f:
            json.dump(func_op_htmls, f, indent=4, ensure_ascii=False)

    data_html_path = os.path.join(dic_path, "DataTypes", "HTMLs.json")
    if os.path.exists(data_html_path):
        print("File " + data_html_path + " exists！")
    else:
        data_htmls = funcs_htmls_crawler(htmls_list["DataTypes"],htmls_list["DataTypes_start"], htmls_list["DataTypes_end"])
        with open(data_html_path, 'w', encoding='utf-8') as f:
            json.dump(data_htmls, f, indent=4, ensure_ascii=False)


    # information crawler and classification
    feature_types = ["Operators", "Functions", "DataTypes"]
    for feature in feature_types:
        htmls_filename = os.path.join(dic_path, feature, "HTMLs.json")
        results_dic = os.path.join(dic_path, feature, "Results")
        results_category_dic = os.path.join(dic_path, feature, "Results_Category")
        crawler_results(feature, htmls_filename, results_dic)
        category_classifier(results_dic, results_category_dic)

tidb_crawler()
