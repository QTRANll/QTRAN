import os
import json
from src.FeatureKnowledgeBaseConstruction.TiDB.HTMLs_Crawler import ops_htmls_crawler, funcs_htmls_crawler
from src.FeatureKnowledgeBaseConstruction.TiDB.Info_Crawler import crawler_results
from src.Tools.Crawler.crawler_options import category_classifier
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)


def tidb_crawler():
    dic_path = os.path.join(current_dir,"..", "..", "..", "FeatureKnowledgeBase", "tidb")
    feature_types = ["datatype", "function", "operator"]
    sub_dic = ["results", "results_category"]
    htmls_list = {
        "function": "https://docs.pingcap.com/zh/tidb/v8.3/json-functions-create",
        "Functions_start": "https://docs.pingcap.com/zh/tidb/v8.3/control-flow-functions",
        "Functions_end": "https://docs.pingcap.com/zh/tidb/v8.3/oracle-functions-to-tidb",
        "operator": "https://docs.pingcap.com/zh/tidb/v8.3/operators",
        "datatype": "https://docs.pingcap.com/zh/tidb/v8.3/data-type-numeric",
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

    # htmls Crawler
    op_html_path = os.path.join(dic_path, "operator", "HTMLs.json")
    if os.path.exists(op_html_path):
        print("File " + op_html_path + " exists！")
    else:
        op_htmls = ops_htmls_crawler(htmls_list["operator"])
        with open(op_html_path, 'w', encoding='utf-8') as f:
            json.dump(op_htmls, f, indent=4, ensure_ascii=False)

    func_html_path = os.path.join(dic_path, "function", "HTMLs.json")
    if os.path.exists(func_html_path):
        print("File " + func_html_path + " exists！")
    else:
        func_op_htmls = funcs_htmls_crawler(htmls_list["function"],htmls_list["Functions_start"], htmls_list["Functions_end"])
        with open(func_html_path, 'w', encoding='utf-8') as f:
            json.dump(func_op_htmls, f, indent=4, ensure_ascii=False)

    data_html_path = os.path.join(dic_path, "datatype", "HTMLs.json")
    if os.path.exists(data_html_path):
        print("File " + data_html_path + " exists！")
    else:
        data_htmls = funcs_htmls_crawler(htmls_list["datatype"],htmls_list["DataTypes_start"], htmls_list["DataTypes_end"])
        with open(data_html_path, 'w', encoding='utf-8') as f:
            json.dump(data_htmls, f, indent=4, ensure_ascii=False)


    # information Crawler and classification
    feature_types = ["operator", "function", "datatype"]
    for feature in feature_types:
        htmls_filename = os.path.join(dic_path, feature, "HTMLs.json")
        results_dic = os.path.join(dic_path, feature, "results")
        results_category_dic = os.path.join(dic_path, feature, "results_category")
        crawler_results(feature, htmls_filename, results_dic)
        category_classifier(results_dic, results_category_dic)