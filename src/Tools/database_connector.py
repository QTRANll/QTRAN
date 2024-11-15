# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/24 9:57
# @Author  : shaocanfan
# @File    : database_connector.py
# @Intro   :

"""
使用sqlalchemy的create_engine方法，连接到不同的数据库，并设置连接池的参数。这里设置了连接池的大小为6，最大溢出数为12。
因为对于oceanbase，SQLALCHEMY没有对应的连接器，所以设置为自行pymysql的方式传值连接
mysql，mariadb，tidb的用法是类似的，tidb默认端口4000
postgres使用Psycopg2的适配器
依赖文件
pip install pymysql
pip install sqlalchemy
pip install psycopg2
"""
'''
DatabaseConnectionPool()   初始化数据库连接池。
Parameters:
    dbType (str): 数据库类型，支持 'MYSQL', 'MARIADB', 'TIDB', 'POSTGRES', 'SQLITE', 'OCEANBASE'。
    host (str): 数据库主机地址。
    port (int): 数据库端口。
    username (str): 数据库用户名。
    password (str): 数据库密码。
    dbname (str): 数据库名称。
    pool_size (int): 连接池大小，默认为 6。
    max_overflow (int): 最大溢出数，默认为 12。

def execSQL(self, query):
        执行 SQL 查询。
        Parameters:
            query (str): 要执行的 SQL 查询语句。
        Returns:
            result (list): 查询结果集合。
            execution_time (float): SQL 查询执行时间（秒）。
'''

import pymysql
from sqlalchemy import create_engine, text, exc
import time
import json
import os
import sqlite3
# import psycopg2
from sqlalchemy.exc import OperationalError
import time
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
import subprocess
import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在目录
current_dir = os.path.dirname(current_file_path)

ddl_path_prefix = os.path.join(current_dir, "..","DLL_Info")

database_connection_args_pinolo = {
    # PINOLO相关的
    "mysql": {
        "db_type": "mysql",
        "host": "127.0.0.1",
        "port": 13306,
        "username": "root",
        "password": "123456",
        "dbname": "PINOLO_MySQL",
        "ddl_filename": "ddl_mysql.json"
    },
    "mariadb": {
        "db_type": "mariadb",
        "host": "127.0.0.1",
        "port": 9901,
        "username": "root",
        "password": "123456",
        "dbname": "PINOLO_MariaDB",
        "ddl_filename": "ddl_mysql.json"
    },
    "tidb": {
        "db_type": "tidb",
        "host": "172.19.42.242",
        "port": 4000,
        "username": "root",
        "password": "123456",
        "dbname": "PINOLO_TiDB",
        "ddl_filename": "ddl_mysql.json"
    },
    "postgres": {
        "db_type": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
        "username": "postgres",
        "password": "123456",
        "dbname": "pinolo_postgressql",
        "ddl_filename": "ddl_postgres.json"
    },
    "sqlite": {
        "db_type": "sqlite",
        "host": "",
        "port": 0,
        "username": "",
        "password": "",
        "dbname": os.path.join(ddl_path_prefix, "PINOLO_SQLite.db"),
        "ddl_filename": "ddl_duckdb.json"
    },
    "duckdb": {
        "db_type": "duckdb",
        "host": "",
        "port": 0,
        "username": "",
        "password": "",
        "dbname":  os.path.join(ddl_path_prefix, "PINOLO_DuckDB.duckdb"),
        "ddl_filename": "ddl_duckdb.json"
    },
    "monetdb": {
        "db_type": "monetdb",
        "host": "127.0.0.1",
        "port": 32768,
        "username": "monetdb",
        "password": "123456",
        "dbname": "PINOLO_MonetDB",
        "ddl_filename": "ddl_monetdb.json"
    },
    "clickhouse": {
        "db_type": "clickhouse",
        "host": "127.0.0.1",
        "port": 8123,
        "username": "admin",
        "password": "123456",
        "dbname": "PINOLO_ClickHouse",
        "ddl_filename": "ddl_clickhouse.json"
    }
}

database_connection_args_sqlancer = {
    # PINOLO相关的
    "mysql": {
        "db_type": "mysql",
        "host": "127.0.0.1",
        "port": 13306,
        "username": "root",
        "password": "123456",
        "dbname": "SQLancer_MySQL",
        "cleardb": "temp",
        "ddl_filename": "ddl_mysql.json"
    },
    "mariadb": {
        "db_type": "mariadb",
        "host": "127.0.0.1",
        "port": 9901,
        "username": "root",
        "password": "123456",
        "dbname": "SQLancer_MariaDB",
        "cleardb": "temp",
        "ddl_filename": "ddl_mysql.json"
    },
    "tidb": {
        "db_type": "tidb",
        "host": "172.19.42.242",
        "port": 4000,
        "username": "root",
        "password": "123456",
        "dbname": "SQLancer_TiDB",
        "cleardb": "temp",
        "ddl_filename": "ddl_mysql.json"
    },
    "postgres": {
        "db_type": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
        "username": "postgres",
        "password": "123456",
        "dbname": "sqlancer_postgressql",
        "cleardb": "temp",
        "ddl_filename": "ddl_postgres.json"
    },
    "sqlite": {
        "db_type": "sqlite",
        "host": "",
        "port": 0,
        "username": "",
        "password": "",
        "dbname":  os.path.join(ddl_path_prefix, "SQLancer_SQLite.db"),
        "cleardb": "",
        "ddl_filename": ""
    },
    "duckdb": {
        "db_type": "duckdb",
        "host": "",
        "port": 0,
        "username": "",
        "password": "",
        "dbname":  os.path.join(ddl_path_prefix, "SQLancer_DuckDB.duckdb"),
        "cleardb": "",
        "ddl_filename": ""
    },
    "monetdb": {
        "db_type": "monetdb",
        "host": "127.0.0.1",
        "port": 32768,
        "username": "monetdb",
        "password": "monetdb",
        "dbname": "SQLancer_MonetDB",
        "cleardb": "temp",
        "ddl_filename": "ddl_monetdb.json"
    },
    "clickhouse": {
        "db_type": "clickhouse",
        "host": "127.0.0.1",
        "port": 8123,
        "username": "admin",
        "password": "123456",
        "dbname": "SQLancer_ClickHouse",
        "cleardb": "temp",
        "ddl_filename": "ddl_clickhouse.json"
    }
}


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
            # 获取连接
            with self.engine.connect() as connection:
                # 执行简单的查询
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
                """
                if self.dbType == "MARIADB":
                    while not self.check_connection():
                        # 强行等待，等待docker恢复连接
                        time.sleep(3)
                """
            elif self.dbType == 'POSTGRES':
                self.engine = create_engine(
                    f'postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}',
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                )
            elif self.dbType == 'MONETDB':
                # 先打开对应的数据库
                subprocess.run(["docker", "exec", "monetdbtest", "monetdb", "start", self.dbname])

                self.engine = create_engine(
                    f'monetdb+pymonetdb://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}',
                    pool_size=self.pool_size,
                )
                """
                self.engine = create_engine(
                    f'monetdb://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}',
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                )
                """
            elif self.dbType == 'SQLITE':
                # For SQLite, it uses a file path, not a typical "host/database" format
                # db_path = f'sqlite:///{self.dbname}.db'
                db_path = f'sqlite:///{self.dbname}'
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
            # clickhouseURI = f"clickhouse+http://{clickhouseConfig.get('username')}:{clickhouseConfig.get('password')}@{clickhouseConfig.get('host')}:{clickhouseConfig.get('port')}/{clickhouseConfig.get('database')}"
            elif self.dbType == 'OCEANBASE':
                # For OceanBase, if SQLAlchemy is not supported, you would use a different mechanism
                self.engine = None
            elif self.dbType == 'DUCKDB':
                # For DuckDB, it uses a file path, not a typical "host/database" format
                # db_path = f'duckdb:///{self.dbname}.duckdb'
                db_path = f'duckdb:///{self.dbname}'
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


# 获取数据库连接所需要的参数
def get_database_connect_params(tool_name, db_type):
    if tool_name.lower() == "pinolo":
        if db_type.lower() not in database_connection_args_pinolo:
            print("数据库信息不存在")
            return
        info = database_connection_args_pinolo[db_type.lower()]
    elif tool_name.lower() == "sqlancer":
        if db_type.lower() not in database_connection_args_sqlancer:
            print("数据库信息不存在")
            return
        info = database_connection_args_sqlancer[db_type.lower()]
    return info


# 测试样例：MySQL / MariaDB / TiDB
def database_define_pinolo(db_type):
    # 创建连接池实例
    info = get_database_connect_params("pinolo", db_type)
    pool = DatabaseConnectionPool(info["db_type"], info["host"], info["port"], info["username"], info["password"], info["dbname"])
    pool.execSQL("DROP TABLE table_3_utf8_undef")
    pool.execSQL("DROP TABLE table_7_utf8_undef")
    pool.execSQL("DROP TABLE dialect_recognize_table")

    with open(os.path.join(ddl_path_prefix, "PINOLO", info["ddl_filename"]), "r", encoding="utf-8") as rf:
        ddls = json.load(rf)
        for ddl in ddls:
            pool.execSQL(ddl)
    pool.close()


def database_define_sqlancer(db_type, ddl_path):
    # 创建连接池实例
    info = get_database_connect_params("sqlancer", db_type)
    pool = DatabaseConnectionPool(info["db_type"], info["host"], info["port"], info["username"], info["password"], info["dbname"])

    with open(os.path.join(ddl_path), "r", encoding="utf-8") as rf:
        ddls = json.load(rf)
        for ddl in ddls:
            pool.execSQL(ddl)
    pool.close()

# sqlancer每次执行后要清除数据库内的所有表格
def database_clear_sqlancer(db_type, db_name):
    # 特殊处理：删除对应的db文件即可
    if db_type.lower() in ["sqlite","duckdb"]:
        if os.path.exists(db_name):
            print("存在"+db_name)
            os.remove(db_name)
            print(f"{db_name} 已删除")
        else:
            print(f"{db_name} 不存在")
    elif db_type.lower() in ["monetdb"]:
        info = get_database_connect_params("sqlancer", db_type)
        container_name = "monetdbtest"
        # 停止数据库
        subprocess.run(["docker", "exec", container_name, "monetdb", "stop", info["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "destroy", "-f", info["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "create", info["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "release", info["dbname"]])
        subprocess.run(["docker", "exec", container_name, "monetdb", "start", info["dbname"]])
        print(db_type + "," + db_name + "重置成功")
    else:
        info = get_database_connect_params("sqlancer", db_type)
        pool = DatabaseConnectionPool(info["db_type"], info["host"], info["port"], info["username"], info["password"],
                                      info["cleardb"])

        with open(os.path.join(ddl_path_prefix, "SQLancer", info["ddl_filename"]), "r", encoding="utf-8") as rf:
            ddls = json.load(rf)

        last_exec_flag = None  # 最后一次执行是否正确
        for ddl in ddls:
            ddl = ddl.replace("db_name", info["dbname"])
            pool.execSQL(ddl)

        print(db_type + "," + db_name + "重置成功")
        pool.close()



def exec_sql_statement(tool_name, db_type, sql_statement):
    # 创建连接池实例
    if tool_name.lower() in ["sqlancer", "sqlright"]:
        tool_name = "sqlancer"
    info = get_database_connect_params(tool_name, db_type)
    pool = DatabaseConnectionPool(info["db_type"], info["host"], info["port"], info["username"], info["password"], info["dbname"])
    result, exec_time, error_message = pool.execSQL(sql_statement)
    pool.close()
    return result, exec_time, error_message