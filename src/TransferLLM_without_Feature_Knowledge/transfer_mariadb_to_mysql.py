# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/1 9:54
# @Author  : shaocanfan
# @File    : test_mariadb_to_mysql.py
# @Intro   :
from TransferLLM import exec_transfer_llm
from TransferLLMEvaluation import evaluate_transfer_llm


# transfer llm
Iteration_Num = 4  # 暂定默认最大迭代次数为三次
Temperature = 0.1
Model = "gpt-4o-mini"
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=False, iteration_num=0, FewShot=False,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=1, len_high=240,
                  IsRandom=False, num=0, sqls_type="origin")
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=False, iteration_num=0, FewShot=True,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=1, len_high=240,
                  IsRandom=False, num=0, sqls_type="origin")
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=False, iteration_num=0, FewShot=False,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=240, len_high=260,
                  IsRandom=False, num=0, sqls_type="origin")
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=False, iteration_num=0, FewShot=True,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=240, len_high=260,
                  IsRandom=False, num=0, sqls_type="origin")

exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=False, iteration_num=0, FewShot=False,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=1,
                  len_high=float('inf'), IsRandom=True, num=500, sqls_type="origin")
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=False, iteration_num=0, FewShot=False,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=1,
                  len_high=float('inf'), IsRandom=True, num=500, sqls_type="simple")
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=False, iteration_num=0, FewShot=True,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=1,
                  len_high=float('inf'), IsRandom=True, num=500, sqls_type="origin")
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=True, iteration_num=Iteration_Num,
                  FewShot=False, output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=1,
                  len_high=float('inf'), IsRandom=True, num=500, sqls_type="origin")
exec_transfer_llm(temperature=Temperature, model=Model, error_iteration=True, iteration_num=Iteration_Num, FewShot=True,
                  output_name="output1", origin_db_name="mariadb", target_db_name="mysql", len_low=1,
                  len_high=float('inf'), IsRandom=True, num=500, sqls_type="simple")

# evaluate transfer llm
Ranges = [[1, float('inf')], [1, 400], [400, 800], [800, 1200], [1200, 1600], [1600, float('inf')]]

evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/ALL/output1_mariadb_to_mysql_1_240_originalSql_all.json", Ranges)
evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/ALL/fewshot_output1_mariadb_to_mysql_1_240_originalSql_all.json", Ranges)
evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/ALL/output1_mariadb_to_mysql_240_260_originalSql_all.json", Ranges)
evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/ALL/fewshot_output1_mariadb_to_mysql_240_260_originalSql_all.json", Ranges)

evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/RANDOM/output1_mariadb_to_mysql_1_inf_originalSql_random_500.json", Ranges)
evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/RANDOM/output1_mariadb_to_mysql_1_inf_originalSqlsim_random_500.json", Ranges)
evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/RANDOM/fewshot_output1_mariadb_to_mysql_1_inf_originalSql_random_500.json", Ranges)
evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/RANDOM/iterated_output1_mariadb_to_mysql_1_inf_originalSql_random_500.json", Ranges)
evaluate_transfer_llm("../../Dataset/Pinolo Output/output_test_results/RANDOM/iterated_fewshot_output1_mariadb_to_mysql_1_inf_originalSqlsim_random_500.json", Ranges)
