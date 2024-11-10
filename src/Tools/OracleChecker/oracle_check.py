from src.Tools.OracleChecker.Result import Result
from typing import Tuple,Sequence
from sqlalchemy.engine.row import Row


def Check(originResult: Result, mutatedResult: Result, isUpper: bool, isSame: bool) -> Tuple[bool, str]:
    cmp, err = originResult.cmp(mutatedResult)
    if err:
        return False, err
    # 相等，则满足oracle
    if isSame:
        if cmp == 0:
            return True, None
        else:
            return False, None
    else:
        if cmp == 0:
            return True, None
        if (isUpper and cmp == -1) or (not isUpper and cmp == 1):
            return True, None
        return False, None


def convert_to_result(data: Sequence[Row]) -> Result:
    if not data:
        return Result(column_names=[], column_types=[], rows=[], err=None)
    
    first_row = data[0]
    column_names = list(first_row.keys())
    
    # 假设所有列的数据类型为字符串
    column_types = ['str' for _ in column_names]
    
    # 将数据行转换为字符串的列表
    rows = [[str(row[key]) for key in column_names] for row in data]
    return Result(column_names=column_names, column_types=column_types, rows=rows)

# 示例用法
def usage_example():
    column_names = ["ID", "Name", "Age"]
    column_types = ["int", "string", "int"]

    rows = [
        ["1", "Alice", "30"],
        ["2", "Bob", "25"],
        ["3", "Charlie", "35"]
    ]

    another_rows = [
        ["2", "Bob", "25"],
        ["3", "Charlie", "35"]
    ]


    # 创建 Result 对象
    result = Result(column_names, column_types, rows)
    another_result = Result(column_names, column_types, another_rows)
    is_upper = True
    end, error = Check(result, another_result, is_upper) # check result->another_result是否符合is_upper
    # Check result: False,check "result->another_result"是否为upper，显然不是故返回false
    if error:
        print(f"Error occurred: {error}")
    else:
        print(f"Check result: {end}")


# 将得到的list结构的sql执行结果，转换格式
def execSQL_result_convertor(exec_result):
    """
    标准格式如下：
            column_names = ["c1", "c2", "c3"]
            column_types = ["int", "string", "int"]
            rows = [
                ["1", "Alice", "30"],
                ["2", "Bob", "25"],
                ["3", "Charlie", "35"]
            ]
    :return:
    """
    converted_result = {
        "column_names": [],
        "column_types": [],
        "rows": []
    }
    if exec_result == None:
        return converted_result
    if len(exec_result) > 0:
        for i in range(len(exec_result[0])):
            converted_result["column_names"].append("c" + str(i))
            converted_result["column_types"].append(type(exec_result[0][i]))

    for item in exec_result:
        temp = []
        for j in range(len(exec_result[0])):
            temp.append(str(item[j]))
        converted_result["rows"].append(temp)
    print(converted_result)
    return converted_result


"""
def oracle_check_testing_dataset(origin_db, target_db, testing_filename, dir_filename):

    with open(testing_filename, "r", encoding="utf-8") as r:
        contents = json.load(r)

    origin_true_cnt = 0
    origin_false_cnt = 0
    target_true_cnt = 0
    target_false_cnt = 0
    for key, value in contents.items():
        for item in value:
            print(item[ "index"])
            # origin db的(origin sql,mutated sql)的oracle check结果
            originalSqlsim = item["originalSqlsim"]
            mutatedSqlsim = item["mutatedSqlsim"]

            # originalSqlsim = item["originalSql"]
            # mutatedSqlsim = item["mutatedSql"]

            ori_result, ori_exec_time, ori_error_message = test_database_postgres(origin_db_args["db_type"], origin_db_args["host"], origin_db_args["port"], origin_db_args["username"], origin_db_args["password"], origin_db_args["dbname"], originalSqlsim)
            mutate_result, mutate_exec_time, mutate_error_message = test_database_postgres(origin_db_args["db_type"], origin_db_args["host"], origin_db_args["port"], origin_db_args["username"], origin_db_args["password"], origin_db_args["dbname"], mutatedSqlsim)
            converted_ori_result = execSQL_result_convertor(ori_result)
            converted_mutate_result = execSQL_result_convertor(mutate_result)

            item["originalSqlsim_"+origin_db+"_result"] = str(ori_result)
            item["originalSqlsim_"+origin_db+"_error"] = str(ori_error_message)
            item["mutatedSqlsim_"+origin_db+"_result"] = str(mutate_result)
            item["mutatedSqlsim_"+origin_db+"_error"] = str(mutate_error_message)

            # 创建 Result 对象
            ori_result_object = Result(converted_ori_result["column_names"], converted_ori_result["column_types"], converted_ori_result["rows"])
            mutate_result_object = Result(converted_mutate_result["column_names"], converted_mutate_result["column_types"], converted_mutate_result["rows"])

            end, error = Check(ori_result_object, mutate_result_object, item["isUpper"])  # check result->another_result是否符合is_upper
            # Check result: False,check "result->another_result"是否为upper，显然不是故返回false
            if error:
                print(f"Error occurred: {error}")
            else:
                print(f"Check result: {end}")

            item[origin_db+"_oracle_check"] = {
                "end": end,
                "error": error
            }

            if end:
                origin_true_cnt += 1
            else:
                origin_false_cnt += 1

            # target db的(origin sql,mutated sql)的oracle check结果
            originalSqlsim = item["originalSqlsim_postgres"]
            mutatedSqlsim = item["mutatedSqlsim_postgres"]["mutated sql"]

            ori_result, ori_exec_time, ori_error_message = test_database_postgres(target_db_args["db_type"], target_db_args["host"], target_db_args["port"], target_db_args["username"], target_db_args["password"], target_db_args["dbname"], originalSqlsim)
            mutate_result, mutate_exec_time, mutate_error_message = test_database_postgres(target_db_args["db_type"], target_db_args["host"], target_db_args["port"], target_db_args["username"], target_db_args["password"], target_db_args["dbname"], mutatedSqlsim)
            converted_ori_result = execSQL_result_convertor(ori_result)
            converted_mutate_result = execSQL_result_convertor(mutate_result)

            item["originalSqlsim_"+target_db+"_result"] = str(ori_result)
            item["originalSqlsim_"+target_db+"_error"] = str(ori_error_message)
            item["mutatedSqlsim_"+target_db+"_result"] = str(mutate_result)
            item["mutatedSqlsim_"+target_db+"_error"] = str(mutate_error_message)

            # 创建 Result 对象
            ori_result_object = Result(converted_ori_result["column_names"], converted_ori_result["column_types"], converted_ori_result["rows"])
            mutate_result_object = Result(converted_mutate_result["column_names"], converted_mutate_result["column_types"], converted_mutate_result["rows"])

            end, error = Check(ori_result_object, mutate_result_object, item["isUpper"])  # check result->another_result是否符合is_upper
            # Check result: False,check "result->another_result"是否为upper，显然不是故返回false
            if error:
                print(f"Error occurred: {error}")
            else:
                print(f"Check result: {end}")

            item[target_db+"_oracle_check"] = {
                "end": end,
                "error": error
            }

            if end:
                target_true_cnt += 1
            else:
                target_false_cnt += 1

    with open(dir_filename, "w", encoding="utf-8") as w:
        json.dump(contents, w, indent=4)

    print("origin true:"+str(origin_true_cnt))
    print("origin false:"+str(origin_false_cnt))
    print("target true:"+str(target_true_cnt))
    print("target false:"+str(target_false_cnt))
"""

if __name__ == "__main__":
    filename = "../../../Dataset/FineTuning/Pinolo FineTuning/TestingDataset/postgres_testing_dataset1.0.jsonl"
    filename_dir = "../../../Dataset/FineTuning/Pinolo FineTuning/OracleCheckerResults/postgres_testing_dataset_oracle_check1.0.jsonl"
    # oracle_check_testing_dataset("mysql", "postgres", filename, filename_dir)