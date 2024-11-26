# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 9:57
# @Author  : shaocanfan
# @File    : database_connector.py
# @Intro   :

import pymysql
from sqlalchemy import text, exc, PoolProxiedConnection
import json
from sqlalchemy.exc import OperationalError
import time
from sqlalchemy import create_engine
import subprocess
import os
from src.Tools.DatabaseConnect.docker_create import run_container
import threading
import sys

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

class DatabaseConnectionPool:
    def __init__(self, dbType, host, port, username, password, dbname, pool_size=20, max_overflow=20):
        self.dbType = dbType.upper()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.engine = None
        self.create_engine()

    # 检查连接是否成功
    def check_connection(self):
        try:
            with self.engine.connect() as connection:
                self.execSQL("SELECT 1;")
            return True
        except OperationalError as e:
            print(f"连接失败: {e}")
            return False

    def create_engine(self):
        try:
            if self.dbType in ['MYSQL', 'MARIADB', 'TIDB']:
                self.engine = create_engine(
                    f'mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}',
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    isolation_level="READ COMMITTED"
                )
            elif self.dbType == 'POSTGRES':
                self.engine = create_engine(
                    f'postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}',
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                )
            elif self.dbType == 'MONETDB':
                self.engine = create_engine(
                    f'monetdb+pymonetdb://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}',
                    pool_size=self.pool_size,
                )
            elif self.dbType == 'SQLITE':
                # For SQLite, it uses a file path, not a typical "host/database" format
                db_path = f'sqlite:///{os.path.join(current_dir, self.dbname)}.db'
                # db_path = f'sqlite:///{self.dbname}'
                self.engine = create_engine(
                    db_path,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow
                )
            elif self.dbType == 'CLICKHOUSE':
                self.engine = create_engine(
                    f"clickhouse+http://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}",
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow
                )
            elif self.dbType == 'OCEANBASE':
                # For OceanBase, if SQLAlchemy is not supported, you would use a different mechanism
                self.engine = None
            elif self.dbType == 'DUCKDB':
                # For duckdb, it uses a file path, not a typical "host/database" format
                db_path = f'duckdb:///{os.path.join(current_dir, self.dbname)}.duckdb'
                # db_path = f'duckdb:///{self.dbname}'
                self.engine = create_engine(
                    db_path,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow
                )
            else:
                raise ValueError("Unsupported database type")
        except exc.SQLAlchemyError as e:
            print(f"Failed to create engine: {e}")
            raise

    def close(self):
        try:
            if self.engine:
                self.engine.dispose()  # Dispose the engine to close all connections
        except Exception as e:
            print(f"Failed to close database connection: {e}")
            raise

    def execSQL(self, query):
        start_time = time.time()  # 开始计时
        affected_rows = 0  # 初始化受影响的行数
        result = None  # 初始化结果为 None
        try:
            if self.dbType == 'OCEANBASE':
                conn = pymysql.connect(host=self.host, port=int(self.port), user=self.username, password=self.password,
                                       database=self.dbname)
                cursor = conn.cursor()
                cursor.execute(query)
                affected_rows = cursor.rowcount
                if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE')):
                    conn.commit()  # 提交事务
                else:
                    result = cursor.fetchall()  # 获取查询结果
                conn.close()
            elif self.dbType == "POSTGRES":
                with self.engine.connect() as connection:
                    # 设置自动提交
                    connection.execution_options(isolation_level="AUTOCOMMIT")
                    res = connection.execute(text(query))
                    affected_rows = res.rowcount
                    if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE')):
                        connection.commit()
                    else:
                        # 对于其他类型的查询，如 SELECT，获取结果
                        result = res.fetchall()
            else:
                with self.engine.connect() as connection:
                    res = connection.execute(text(query))
                    affected_rows = res.rowcount
                    if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE', 'CREATE')):
                        connection.commit()
                    else:
                        # 对于其他类型的查询，如 SELECT，获取结果
                        result = res.fetchall()
            end_time = time.time()  # 结束计时
            execution_time = end_time - start_time  # 计算执行时间
            print("Affected rows:", affected_rows)
            return result, execution_time, None  # 返回结果和执行时间
        except Exception as e:
            error_message = f"Error executing '{query}':" + str(e)
            print(f"Error executing '{query}':", e)
            # return None, 0 , error_message
            return None, 0, str(e)


# 每次执行后要清除数据库内的所有表格
def database_clear(tool, exp, dbType):
    args = get_database_connector_args(dbType.lower())
    args["dbname"] = f"{tool}_{exp}_{dbType}".lower() if "tlp" not in exp else f"{tool}_tlp_{dbType}".lower()
    # 特殊处理：删除对应的db文件即可
    if dbType.lower() in ["sqlite"]:
        db_filepath = os.path.join(current_dir,f'{args["dbname"]}.db')
        if os.path.exists(db_filepath):
            print(db_filepath)
            os.remove(db_filepath)
            print(db_filepath +"已删除")
        else:
            print(db_filepath+"不存在")
    elif dbType.lower() in ["duckdb"]:
        db_filepath = os.path.join(current_dir, f'{args["dbname"]}.duckdb')
        if os.path.exists(db_filepath):
            print(db_filepath)
            os.remove(db_filepath)
            print(db_filepath +"已删除")
        else:
            print(db_filepath+"不存在")
    elif dbType.lower() in ["monetdb"]:
        container_name = args["container_name"]
        # 停止数据库
        subprocess.run(["docker", "exec", container_name, "monetdb", "stop", args["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "destroy", "-f", args["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "create", args["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "release", args["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "start", args["dbname"]])
        print(dbType + "," + args["dbname"] + "重置成功")
    else:
        pool = DatabaseConnectionPool(args["dbType"], args["host"], args["port"], args["username"], args["password"],  f"{tool.lower()}_temp_{dbType.lower()}")
        with open(os.path.join(current_dir,"database_clear", dbType.lower() + ".json"), "r", encoding="utf-8") as rf:
            ddls = json.load(rf)
        for ddl in ddls:
            ddl = ddl.replace("db_name", args["dbname"])
            pool.execSQL(ddl)
        print(args["dbname"] + "重置成功")
        pool.close()

def exec_sql_statement(tool, exp, dbType, sql_statement):
    # 创建连接池实例
    if tool.lower() in ["sqlancer", "sqlright"]:
        tool = "sqlancer"
    args = get_database_connector_args(dbType.lower())

    args["dbname"] = f"{tool}_{exp}_{dbType}".lower() if "tlp" not in exp else f"{tool}_tlp_{dbType}".lower()
    # 先检查容器是否打开，即数据库是否能正常链接，如果没有正常链接则打开容器
    pool = DatabaseConnectionPool(args["dbType"], args["host"], args["port"], args["username"], args["password"], args["dbname"])

    if dbType not in ["clickhouse"] and not pool.check_connection():
        run_container(tool, exp, dbType)
    result, exec_time, error_message = pool.execSQL(sql_statement)
    pool.close()
    return result, exec_time, error_message


def run_with_timeout(func, timeout, *args, **kwargs):
    result = [None, None, None]  # 使用列表来存储返回值，因为列表是可变的

    def thread_func():
        result[0], result[1], result[2] = func(*args, **kwargs)

    thread = threading.Thread(target=thread_func)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # 若线程未完成则中断并抛出超时异常
        thread.join()  # 等待线程结束
        raise TimeoutError("Function call timed out.")

    return result[0], result[1], result[2]  # 返回函数的执行结果

def database_define_pinolo(tool, exp, dbType):
    # 创建连接池实例
    args = get_database_connector_args(dbType.lower())
    args["dbname"] = f"{tool}_{exp}_{dbType}"
    pool = DatabaseConnectionPool(args["dbType"], args["host"], args["port"], args["username"], args["password"], args["dbname"])
    with open(os.path.join(current_dir, tool.lower(), exp.lower(), dbType.lower()+".json"), "r", encoding="utf-8") as rf:
        ddls = json.load(rf)
        for ddl in ddls:
            pool.execSQL(ddl)
    pool.close()


def get_database_connector_args(dbType):
    with open(os.path.join(current_dir, "database_connector_args.json"), "r", encoding="utf-8") as r:
        database_connection_args = json.load(r)
    if dbType.lower() in database_connection_args:
        return database_connection_args[dbType.lower()]

def database_connect_test():
    # 1.PINOLO
    # database_define_pinolo('pinolo', 'exp1','mysql')
    # database_define_pinolo('pinolo', 'exp1','mariadb')
    # database_define_pinolo('pinolo', 'exp1', 'tidb')
    # database_define_pinolo('pinolo', 'exp1','sqlite')
    # database_define_pinolo('pinolo', 'exp1','postgres')
    # database_define_pinolo('pinolo', 'exp1',"duckdb")
    # database_define_pinolo('pinolo', 'exp1',"monetdb")
    # database_define_pinolo('pinolo', 'exp1',"clickhouse")



    # 1.PINOLO
    # mysql
    sql_statement = "SELECT (~MONTHNAME(_UTF8MB4'2011-04-18')) AS `f1`,(`f4`) AS `f2`,(CEILING(6)) AS `f3` FROM (SELECT `col_char(20)_key_signed` AS `f4`,`col_bigint_undef_signed` AS `f5`,`col_double_undef_unsigned` AS `f6` FROM `table_3_utf8_undef`) AS `t1`"
    # print(exec_sql_statement('pinolo', 'exp1','mysql', sql_statement))  #TEST OK

    # Mariadb
    sql_statement = "SELECT json_array_intersect(@json1, @json2);"
    # print(exec_sql_statement('pinolo', 'exp1','mariadb', sql_statement))  # TEST OK
    sql_statement = "SELECT 1;"
    # print(exec_sql_statement('pinolo', 'exp1','mariadb', sql_statement))  # TEST OK

    # tidb
    # print(exec_sql_statement("pinolo", 'exp1','tidb', sql_statement))  # TEST OK

    # SQLite
    sqlite_sql = "SELECT * FROM table_3_utf8_undef;"
    # print(exec_sql_statement("pinolo", 'exp1','sqlite', sqlite_sql))  # TEST OK

    # postgres
    postgres_sql = "SELECT (f4) AS f1, (~CAST(CAST(PI() AS numeric) AS int)) AS f2, (-EXTRACT(DOY FROM DATE '2004-05-01')) AS f3 FROM (SELECT col_bigint_key_unsigned AS f4, col_char_20_undef_signed AS f5, col_float_key_signed AS f6 FROM table_3_utf8_undef) AS t1"
    # print(exec_sql_statement("pinolo", 'exp1','postgres', postgres_sql))  # TEST OK

    # duckdb
    duckdb_sql = "SELECT * FROM table_3_utf8_undef;"
    # print(exec_sql_statement("pinolo",'exp1', 'duckdb', duckdb_sql))  # TEST OK

    # monetdb
    monetdb_sql = "SELECT * FROM table_3_utf8_undef;"
    # print(exec_sql_statement("pinolo",'exp1', 'monetdb', monetdb_sql))  # TEST OK

    # clickhouse
    clickhouse_sql = "SELECT * FROM table_3_utf8_undef;"
    # print(exec_sql_statement("pinolo",'exp1', 'clickhouse', clickhouse_sql))  # TEST OK


    # 1.sqlancer
    # mysql
    sqls = [
            "CREATE TABLE t0(c0 INT UNIQUE, c1 INT, c2 INT, c3 INT UNIQUE) ENGINE = MyISAM;",
            "INSERT INTO t0(c0) VALUES(DEFAULT), (\"a\");",
            "INSERT IGNORE INTO t0(c3) VALUES(\"a\"), (1);",
            "REPLACE INTO t0(c1, c0, c3) VALUES(1, 2, 3), (1, \"a\", \"a\");",
            "SELECT (NULL) IN (SELECT t0.c3 FROM t0 WHERE t0.c0);"
    ]
    """
    for sql in sqls:
        print(sqls.index(sql))
        print(exec_sql_statement("sqlancer",'exp1', 'mysql', sql))  #TEST OK
    print(database_clear_sqlancer("sqlancer",'exp1', 'mysql'))
    print(exec_sql_statement("sqlancer", 'exp1', 'mysql', "SHOW TABLES;"))
    """

    # Mariadb
    sqls = [
            "CREATE TABLE t0(c0 INT);",
            "INSERT INTO t0 VALUES (1);",
            "CREATE INDEX i0 ON t0(c0);",
            "SELECT * FROM t0 WHERE 0.5 = c0; -- unexpected: row is fetched"
    ]
    """
    for sql in sqls:
        print(sqls.index(sql))
        print(exec_sql_statement("sqlancer", 'exp1','mariadb', sql))  # TEST OK
    database_clear_sqlancer("sqlancer",'exp1', 'mariadb')
    print(exec_sql_statement("sqlancer", 'exp1', 'mariadb', "SHOW TABLES;"))
    """

    # tidb
    sqls = [
            "CREATE TABLE t0(c0 INT, c1 TEXT AS (0.9));",
            "INSERT INTO t0(c0) VALUES (0);",
            "SELECT 0 FROM t0 WHERE false UNION SELECT 0 FROM t0 WHERE NOT t0.c1; -- expected: {0}, actual: {}"
    ]
    """
    for sql in sqls:
        print(sqls.index(sql))
        print(exec_sql_statement("sqlancer",'exp1','tidb', sql))  #TEST OK
    database_clear_sqlancer("sqlancer", 'exp1','tidb')
    print(exec_sql_statement("sqlancer", 'exp1', 'tidb', "SHOW TABLES;"))
    """


    # SQLite
    sqls = [
        "CREATE TABLE t0(c0 INT UNIQUE);",
        "INSERT INTO t0(c0) VALUES (1);",
        "SELECT * FROM t0 WHERE '1' IN (t0.c0); -- unexpected: fetches row"
    ]
    """
    for sql in sqls:
        print(sqls.index(sql))
        print(exec_sql_statement("sqlancer",'exp1','sqlite', sql))  #TEST OK
    database_clear_sqlancer("sqlancer", 'exp1','sqlite')
    """

    # postgres:sqlancer中无支持的postgres的tlp和norec bug
    sqls = [
            "CREATE TABLE t0(c0 INT);",
            "INSERT INTO t0(c0) VALUES(0), (0);"
    ]
    """
    for sql in sqls:
        print(sqls.index(sql))
        print(exec_sql_statement("sqlancer",'exp1','postgres', sql))  #TEST OK
    database_clear_sqlancer("sqlancer", 'exp1','postgres')
    """

    # duckdb:同sqlite
    sqls = [
            "CREATE TABLE t0(c0 INT);",
            "INSERT INTO t0(c0) VALUES (0);",
            "SELECT * FROM t0 WHERE NOT(NULL OR TRUE); -- expected: {}, actual: {1}"
    ]
    """
    for sql in sqls:
        print(sqls.index(sql))
        print(exec_sql_statement("sqlancer",'exp1','duckdb', sql))  #TEST OK
    database_clear_sqlancer("sqlancer", 'exp1','duckdb')
    """


    # monetdb
    sqls = [
        "CREATE TABLE t0(c0 INT);",
        "INSERT INTO t0(c0) VALUES (0);",
        "SELECT * FROM t0;"
    ]
    """
    for sql in sqls:
        print(sqls.index(sql))
        print(sql)
        print(exec_sql_statement("sqlancer",'exp1','monetdb', sql))  #TEST OK
    database_clear_sqlancer("sqlancer", 'exp1','monetdb')
    """

    # clickhouse
    sqls = [
            "CREATE TABLE t0 (c0 Int32) ENGINE = MergeTree() ORDER BY c0;",
            "INSERT INTO t0 VALUES (1);",
            "SELECT * FROM t0 WHERE c0 = 1;"
    ]
    for sql in sqls:
        print(sqls.index(sql))
        print(exec_sql_statement("sqlancer",'exp1','clickhouse', sql))  #TEST OK
    print(database_clear("sqlancer",'exp1','clickhouse'))

exec_sql_statement("pinolo", "exp1", "clickhouse", "SELECT 1;")