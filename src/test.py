import json
import re
import requests
import os
from src.Connector import ddl_database_mysql_like, test_database_mysql_like

# ddl_database_mysql_like('mysql', '127.0.0.1', 13306, 'root', '123456', 'SQLancerMySQLTLP',"../Dataset/SQLancer Output/ddl_mysql_TLP1.0.json")
sql_statement = "SELECT ALL t0.c0 AS ref0 FROM t0;"
sql_statement = "SELECT ALL t0.c0 AS ref0 FROM t0 WHERE ((t0.c0) LIKE (t0.c0)) LIKE (CAST(COALESCE(NULL, NULL) AS SIGNED)) UNION ALL SELECT t0.c0 AS ref0 FROM t0 WHERE (! (((t0.c0) LIKE (t0.c0)) LIKE (CAST(COALESCE(NULL, NULL) AS SIGNED)))) UNION ALL SELECT t0.c0 AS ref0 FROM t0 WHERE (((t0.c0) LIKE (t0.c0)) LIKE (CAST(COALESCE(NULL, NULL) AS SIGNED))) IS NULL;"
# test_database_mysql_like('mysql', '127.0.0.1', 13306, 'root', '123456', 'database7', sql_statement)  #TEST OK

sql_statement = "SELECT ALL t0.c0 AS ref0 FROM t0;"
ddl_database_mysql_like('postgres','127.0.0.1', 5432, 'postgres', '123456', "database7","../Dataset/SQLancer Output/ddl_postgres_TLP1.0.json")
test_database_mysql_like('postgres', '127.0.0.1', 5432, 'postgres', '123456', 'database7', sql_statement)  #TEST OK


sqls = []
dic_name = "../Dataset/SQLancer Output/mysql_TLP"
filenames = os.listdir(dic_name)
"""
for filename in filenames:
    if "json" not in filename:
        continue
    with open(os.path.join(dic_name, filename), "r", encoding="utf-8") as r:
        result = json.load(r)
    if result["initial_sql"] not in sqls:
        sqls.append(result["initial_sql"])
print(sqls)
"""