# 1 Overview
# 1.1 Setup
## test data

| Fuzzer     | Supported DBMS                             | Extendted                                               |
| ---------- | ------------------------------------------ | ------------------------------------------------------- |
| NoRec(230) | SQLite(41), MariaDB(5), PostgreSQL(0)      | MySQL,TiDB, MonetDB, DuckDB, ClickHouse, (OceanBase)    |
| TLP(304)   | TiDB(31), DuckDB(30), MySQL(10), SQLite(5) | MariaDB, PostgresSQL, MonetDB, ClickHouse,  (OceanBase) |
|            |                                            |                                                         |

给的sqlancer生成的句子有以下几种类别

| Fuzzer | Supported DBMS                  | Extendted                               |
| ------ | ------------------------------- | --------------------------------------- |
| NoRec  | SQLite, PostgreSQL              | MySQL,TiDB, MonetDB, DuckDB, ClickHouse |
| TLP    | TiDB, MySQL, SQLite,PostgresSQL | MariaDB, MonetDB, ClickHouse, DuckDB    |
|        |                                 |                                         |
重点关注：monetdb，tidb，duckdb，clickhouse

# 1.2 Procedure
针对sqlancer的两种策略进行extend，extend experiment步骤大致如下。
1. Step1: rag_based_feature_mapping。先做以下mapping，SQLite/MariaDB/（Postgres是0暂时不弄）mapping to MySQL/TiDB/MonetDB/DuckDB/ClickHouse  
2. Step2: potential_features_refiner,将得到的结果存储到input文件夹中作为输入
3. Step3: 将bug report进行transfer并存储到output文件夹中
4. Step4: mutate llm,将transfer后的最后一句select语句进行mutate并返回结果
5. Step5: check oracle,执行mutate后sql并记录执行结果以及oracle check结果
6. Step6: 筛选出suspicious logic bugs

# 1.3 test
需要将ddl语句先布置好，在执行完清空
## NoREC
1. SQLite -> TiDB, MonetDB, DuckDB, ClickHouse, MySQL


2. Postgres -> TiDB, MonetDB, DuckDB, ClickHouse, MySQL


## TLP
不确定是哪种