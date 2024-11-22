from src.FeatureKnowledgeBaseConstruction.TiDB.tidb_crawler import tidb_crawler
from src.FeatureKnowledgeBaseConstruction.ClickHouse.clickhouse_crawler import clickhouse_crawler
from src.FeatureKnowledgeBaseConstruction.DuckDB.duckdb_crawler import duckdb_crawler
from src.FeatureKnowledgeBaseConstruction.MariaDB.mariadb_crawler import mariadb_crawler
from src.FeatureKnowledgeBaseConstruction.MonetDB.monetdb_crawler import monetdb_crawler
from src.FeatureKnowledgeBaseConstruction.MySQL.mysql_crawler import mysql_crawler
from src.FeatureKnowledgeBaseConstruction.Postgres.postgres_crawler import postgres_crawler
from src.FeatureKnowledgeBaseConstruction.SQLite.sqlite_crawler import sqlite_crawler

def knowledge_base_crawl():
    clickhouse_crawler()
    duckdb_crawler()
    mariadb_crawler()
    monetdb_crawler()
    mysql_crawler()
    postgres_crawler()
    sqlite_crawler()
    tidb_crawler()