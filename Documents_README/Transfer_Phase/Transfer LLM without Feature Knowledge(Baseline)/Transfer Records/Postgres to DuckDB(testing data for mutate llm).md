
* ***Duckdb 的 SQL parser基于 PostgreSQL parser，但 duckdb 并不支持 PostgreSQL 中的所有功能。`duckdb_engine`dialect 是从 `postgresql`dialect 派生而来的。
* mysql transfer to postgres的100 x 4条数据，有很大一部分可以在DuckDB中执行通过，考虑将执行通过的测试数据项直接作为DuckDB的测试数据，将剩余执行失败的数据项postgres transfer to duckdb。

## Connector（DuckDB部分）
1.  ddl：从mysql的ddl修改得到，显示建表结果和mysql的一致
2. connector代码
```Python
# create_engine添加
elif self.dbType == 'DUCKDB':  
    # For DuckDB, it uses a file path, not a typical "host/database" format  
    db_path = f'duckdb:///{self.dbname}.duckdb'  
    self.engine = create_engine(  
        db_path,  
        pool_size=self.pool_size,  
        max_overflow=self.max_overflow  
    )

def test_database_duckdb(dbname, duckdb_statement):  
    # 创建连接池实例  
    pool = DatabaseConnectionPool('duckdb', '', '', '', '', dbname)  
    result, exec_time, error_message = pool.execSQL(duckdb_statement)  
    # 输出结果和执行时间  
    print("查询结果:", result)  
    print("执行时间:", exec_time)  
    return result, exec_time, error_message
```

## Transfer LLM（DuckDB部分）
 1. few-shot：以mysql->postgres的fewshot为原型，给出三个postgres->duckdb的例子
 2. 数据集大小：是从MySQL->postgres转变得到的postgres语句，100 x 4

```
# 检查postgres的100 x 4 条测试数据中，有多少条测试数据可以直接在duckdb中运行  
# postgres_testing_dataset_raw2.0(FixMDistinctL).jsonl:17/100  
# postgres_testing_dataset_raw2.0(FixMCmpOpU).jsonl:59/100  
# postgres_testing_dataset_raw2.0(FixMHaving1U).jsonl:64/100  
# postgres_testing_dataset_raw2.0(FixMOn1U).jsonl:47/100  
  
```
## Mutate LLM（DuckDB部分）
1. mutate llm的微调和测试数据：从postgres的80+80条数据进行转换
```
# 检查mutate llm关于postgres的训练集和测试集中，有多少数据可以直接在duckdb中运行  
# postgres_training_dataset1.0.jsonl:32/80  
# postgres_testing_dataset1.0.jsonl:43/80  
```






