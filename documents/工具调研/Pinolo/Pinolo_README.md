# impomysql

[![Go Reference](https://pkg.go.dev/badge/github.com/qaqcatz/impomysql.svg)](https://pkg.go.dev/github.com/qaqcatz/impomysql)

Detecting Logic Bugs in mysql through Implication Oracle.

Also supports DBMS compatible with mysql syntax, such as mariadb, tidb, oceanbase.

**Note that 'impomysql' is our original name, now you can also call it PINOLO. We may create a new repository in the future.** 

## 1. What is logical bug

See this bug report as an example:

https://bugs.mysql.com/bug.php?id=108937

In theory, the result of sql1 ⊆ the result of sql2:

```sql
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING f1 != 0; -- sql1
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING 1; -- sql2
```

Because the `HAVING 1` in sql2 is always true, but the `HAVING f1 != 0` in sql1 may be false. 

However, the date value changed after changing `HAVING f1 != 0` to `HAVING 1`, this is a logical bug:

```sql
mysql> SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING f1 != 0; -- sql1
+------------+
| f1         |
+------------+
| -1928.8181 |
|  -1995.009 |
|      -2007 |
+------------+
3 rows in set (0.00 sec)

mysql> SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING 1; -- sql2
+---------------------+
| f1                  |
+---------------------+
| -20080524235820.816 |
| -20080524235887.008 |
|     -20080524235899 |
+---------------------+
3 rows in set (0.00 sec)
```

## 2. What is Implication Oracle

In the above example:

```sql
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING f1 != 0; -- sql1
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING 1; -- sql2
```

We changed `HAVING f1 != 0`  to `HAVING 1`.

In theory, the predicate of sql1 → the predicate of sql2, and the result of sql1 ⊆ the result of sql2. 

If the actual result does not satisfy this relationship, we consider that there is a logical bug.

You can see our paper for more details:

```shell
@inproceedings{hao2023pinolo,
  title={Pinolo: Detecting Logical Bugs in Database Management Systems with Approximate Query Synthesis},
  author={Hao, Zongyin and Huang, Quanfeng and Wang, Chengpeng and Wang, Jianfeng and Zhang, Yushan and Wu, Rongxin and Zhang, Charles},
  booktitle={2023 USENIX Annual Technical Conference (USENIX ATC 23)},
  pages={345--358},
  year={2023}
}
```

You can also see the source code:

* mutation/doc.go

* mutation/stage1/doc.go

* mutation/stage2/doc.go

* mutation/stage2/mutatevisitor.go

* resources/impo.yy

## 3. How to use

### 3.1 build

It is recommended to use `golang 1.16.2` ([how to install golang 1.16.2](https://github.com/qaqcatz/impomysql/blob/main/documents/installgo.md)).

```shell
git clone --depth=1 https://github.com/qaqcatz/impomysql.git
cd impomysql
go build
```

**In the following we will refer to the path of `impomysql` as `${IMPOHOME}`**

Now you will see an executable file `${IMPOHOME}/impomysql`.

### 3.2 start your DBMS

For example, you can start mysql with docker:

```shell
sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30
```

You can also compile and install the DBMS yourself.

### 3.3 run task

We consider a DBMS test as a `task`.

#### quick start

We assume you have executed `sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30`

```shell
cd ${IMPOHOME}
./impomysql task ./resources/taskconfig.json
```

If everything is ok, there will be nothing in the terminal, and you will get a new directory `${IMPOHOME}/output/mysql/task-1`, whose structure is as follows:

```shell
${IMPOHOME}/output/mysql/task-1
  |-- bugs
     |-- bug-0-0-FixMHaving1U.log
     |-- bug-0-0-FixMHaving1U.json
  |-- result.json
  |-- task.log
```

You will see a directory named `bugs` in `${IMPOHOME}/output/mysql/task-1`, and two files named `bug-0-0-FixMHaving1U.log` and `bug-0-0-FixMHaving1U.json` respectively in `bugs`. This is the logical bugs we detected. You can take a look at these files yourself first, and we will explain the details of input and output in the following text.

#### input

Command:

```shell
impomysql task <task configuration json file>
```

You only need to provide a configuration file. We will take `${IMPOHOME}/resources/raskconfig.json` as an example:

```json
{
  "outputPath": "./output",
  "dbms": "mysql",
  "taskId": 1,
  "host": "127.0.0.1",
  "port": 13306,
  "username": "root",
  "password": "123456",
  "dbname": "TEST",
  "seed": 123456,
  "ddlPath": "./resources/ddl.sql",
  "dmlPath": "./resources/dml.sql"
}
```

| option                                           | description                                                  |
| ------------------------------------------------ | ------------------------------------------------------------ |
| `outputPath`, `dbms`, `taskId`                   | We will save the result in `outputPath`/`dbms`/task-`taskId` (`taskId` >= 0). <br>We will remove the old directory and create a new directory. <br>If you want to provide a relative path, remember that the path is relative to the directory where you ran the command, not the path of this configuration file. |
| `host`, `port`, `username`, `password`, `dbname` | We will create a database connector with dsn `username`:`password`@tcp(`host`:`port`)/`dbname`, <br>and init database `dbname`. |
| `seed`                                           | Random seed. If seed <= 0, we will use the current time.     |
| `ddlPath`                                        | Sql file responsible for creating data. <br>See `${IMPOHOME}/resources/ddl.sql` as an example. |
| `dmlPath`                                        | Sql file responsible for querying data. <br>We only focus on `SELECT` statements in your `dmlPath`, which means we will ignore some of your sqls such as `EXPLAIN`, `PREPARE` ... <br>See `${IMPOHOME}/resources/dml.sql` as an example. |

#### output

| file                                    | description                                                                                                                                                                                                                                                                     |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| bug-`bugId`-`sqlId`-`mutationName`.log  | Save the mutation name, original sql, original result, mutated sql, mutated result, and the relationship(`IsUpper`) between the original result and the mutated result we expect. `[IsUpper] true` means that the mutated result  should ⊆ the original result.（这边是否有误？）        |
| bug-`bugId`-`sqlId`-`mutationName`.json | Json format of bug-`bugId`-`sqlId`-`mutationName`.log                                                                                                                                                                                                                           |
| `task.log`                              | Task log file, from which you can get task progress and error message.                                                                                                                                                                                                          |
| `result.json`                           | If a task executes successfully, we will create a result file, from which you can get the task's start time(`startTime`), end time(`endTime`), and the number of logical bugs we detected(`impoBugsNum`).<br>The remaining fields are used for our debugging, just ignore them! |

IsUpper: ((candidate.U^candidate.Flag)^1) == 1, U和Flag相同，同为0或同为1时，IsUpper=True； U和Flag不相同，IsUpper=False

U=1，Flag=1，小->大，IsUpper=True
U=1，Flag=0，大->小，IsUpper=False
U=0，Flag=1，大->小，IsUpper=False
U=0，Flag=0，小->大，IsUpper=True


### 3.4 run task with go-randgen

A `task` can automatically generate `ddlPath` and `dmlPath` with the help of [go-randgen](https://github.com/pingcap/go-randgen), you need to build it first.

#### build go-randgen

```shell
git clone https://github.com/pingcap/go-randgen.git
cd go-randgen
go get -u github.com/jteeuwen/go-bindata/...
# make sure you have added GOPATH/bin to your environment variable PATH
make all
```

Now you will see an executable file `go-randgen`, copy it to `${IMPOHOME}/resources`.

#### quick start

We assume you have executed `sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30`

```shell
cd ${IMPOHOME}
./impomysql task ./resources/taskrdgenconfig.json
```

If everything is ok, there will be nothing in the terminal, and you will get a new directory `${IMPOHOME}/output/mysql/task-1`, whose structure is as follows:

```shell
${IMPOHOME}/output/mysql/task-1
  |-- bugs
     |-- bug-0-0-FixMHaving1U.log
     |-- bug-0-0-FixMHaving1U.json
  |-- result.json
  |-- task.log
  |-- output.data.sql
  |-- output.rand.sql
```

Except for the standard output of a task (i.e., bugs, task.log, result.json), you will also see two sql files `output.data.sql`, `output.rand.sql`, which are the `ddlPath` and `dmlPath` automatically generated by `go-randgen`.

#### input

Take `${IMPOHOME}/resources/taskrdgenconfig.json` as an example. We removed `ddlPath` and `dmlPath`, added `randGenPath`, `zzPath`, `yyPath`, `queriesNum`, `needDML`:

```json
{
  "outputPath": "./output",
  "dbms": "mysql",
  "taskId": 1,
  "host": "127.0.0.1",
  "port": 13306,
  "username": "root",
  "password": "123456",
  "dbname": "TEST",
  "seed": 123456,
  "rdGenPath": "./resources/go-randgen",
  "zzPath": "./resources/impo.zz.lua",
  "yyPath": "./resources/impo.yy",
  "queriesNum": 100,
  "needDML": true
}
```

| option             | description                                                  |
| ------------------ | ------------------------------------------------------------ |
| `randGenPath`      | The path of your go-randgen executable file                  |
| `zzPath`, `yyPath` | `go-randgen`  will generate a ddl sql file `output.data.sql` according to `zzPath`, and generate a dml sql file  `output.rand.sql` according to `yyPath`. <br>We have provided a default zz file `impo.zz.lua` and a default yy file `impo.yy` in `${IMPOHOME}/resources`. It is recommended to use these default files. <br>We actually execute the following command: `cd outputPath/dbms/task-taskId && randGenPath gentest -Z zzPath -Y yyPath -Q queriesNum --seed seed -B` |
| `queriesNum`       | The number of sqls in `output.rand.sql`.                     |
| `needDML`          | if `needDML` is false, we will delete `output.rand.sql` at the end of `task` .  It is recommended to set this value to false, because the size of `output.rand.sql` is usually very large(about 10MB with 10000 sqls). |

Note that If you used both (non empty) `rdGenPath` and `ddlPath`, `dmlPath`, we will run `task` with `go-randgen`, and set `ddlPath` to  `outputPath/dbms/task-taskId/output.data.sql`, set `dmlPath` to `outputPath/dbms/task-taskId/output.rand.sql`.

#### output

Except for `bugs`, `task.log`, `result.json`, you will also see `output.data.sql`, `output.rand.sql`.

Of course, if you set `needDML` to false, we will delete `output.rand.sql`.

### 3.5 run task pool

`taskpool` can continuously run tasks in parallel. Make sure you can run task with [go-randgen](https://github.com/pingcap/go-randgen).

#### quick start

We assume you have executed `sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30`

```shell
cd ${IMPOHOME}
./impomysql taskpool ./resources/taskpoolconfig.json
#output:
#time="2023-05-10T15:05:47+08:00" level=info msg="Running **************************************************"
#time="2023-05-10T15:05:47+08:00" level=info msg="Run task0"
#time="2023-05-10T15:05:47+08:00" level=info msg="Run task1"
#time="2023-05-10T15:05:47+08:00" level=info msg="Run task2"
#time="2023-05-10T15:05:47+08:00" level=info msg="Run task3"
#time="2023-05-10T15:05:49+08:00" level=info msg="task-0 detected a logical bug!!! bugId = 0 sqlId = 21 mutationName = FixMHaving1U"
#time="2023-05-10T15:05:51+08:00" level=info msg="task1 Finished"
#time="2023-05-10T15:05:51+08:00" level=info msg="Run task4"
...
#time="2023-05-10T15:06:02+08:00" level=info msg="task15 Finished"
#time="2023-05-10T15:06:02+08:00" level=info msg="max tasks!"
#time="2023-05-10T15:06:02+08:00" level=info msg="Finished **************************************************"
```

If everything is ok, you will get a new directory `${IMPOHOME}/output/mysql`, whose structure is as follows:

```shell
${IMPOHOME}/output/mysql/task-1
  |-- result.json
  |-- taskpool.log
  |-- task-0
     |-- bugs
        |-- bug-0-0-FixMHaving1U.log
        |-- bug-0-0-FixMHaving1U.json
     |-- result.json
     |-- task.log
     |-- output.data.sql
  |-- task-0-config.json
  |-- task-1
     |-- ...
  |-- task-1-config.json
  |-- ...
```

`taskpool` will generate a series of task configurations and run the corresponding tasks based on these configurations. We will explain the details of input and output in the following text.

#### input

Take `${IMPOHOME}/resources/taskpoolconfig.json` as an example:

```json
{
  "outputPath": "./output",
  "dbms": "mysql",
  "host": "127.0.0.1",
  "port": 13306,
  "username": "root",
  "password": "123456",
  "dbPrefix": "TEST",
  "seed": 123456,
  "randGenPath": "./resources/go-randgen",
  "zzPath": "./resources/impo.zz.lua",
  "yyPath": "./resources/impo.yy",
  "queriesNum": 100,
  "threadNum": 4,
  "maxTasks": 16,
  "maxTimeS": 60
}
```

| option      | description                                                  |
| ----------- | ------------------------------------------------------------ |
| `threadNum` | The number of threads                                        |
| `maxTasks`  | Maximum number of tasks, <= 0 means no limit.                |
| `maxTimeS`  | Maximum time(second), <=0 means no limit.                    |
| `dbPrefix`  | For each thread we will create a database connector, the dbname of each connector is `dbPrefix`+thread id. |
| `seed`      | The seed of each task is `seed`+task id.                     |

Note that:

* We will set `needDML` to false.
* It is recommended to set `queriesNum` to a large value(>=10000, a task with `queriesNum`=10000 will take about 5~10 minutes), otherwise you will get a lot of task directories.

#### output

| option                    | description                                                                                                                                                                                                                                                                                                      |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| task-`taskId`-config.json | The configuration file of task-`taskId`.                                                                                                                                                                                                                                                                         |
| `taskpool.log`            | Taskpool log file, from which you can get taskpool progress and error message.                                                                                                                                                                                                                                   |
| `result.json`             | If the taskpool executes successfully, we will create a result file, from which you can get the taskpool's start time(`startTime`), end time(`endTime`), the number of logical bugs we detected(`bugsNum`) and their taskId(`bugTaskIds`).<br>The remaining fields are used for our debugging, just ignore them! |

#### test dbms

We provide default configuration files for mysql, mariadb, tidb, oceanbase, you can follow these configuration files to test your own database.

1. mysql
   
   ```shell
   # sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30
   # see https://hub.docker.com/_/mysql/tags
   # or build it yourself
   # see https://github.com/mysql/mysql-server
   ./impomysql taskpool ./resources/testmysql.json
   ```

2. mariadb
   
   ```shell
   # sudo docker run -itd --name mariadbtest -p 23306:3306 -e MYSQL_ROOT_PASSWORD=123456 --privileged=true mariadb:10.11.1-rc
   # see https://hub.docker.com/_/mariadb/tags
   # or build it yourself
   # see https://github.com/MariaDB/server
   ./impomysql taskpool ./resources/testmariadb.json
   ```

3. tidb
   
   ```shell
   # sudo docker run -itd --name tidbtest -p 4000:4000 pingcap/tidb:v6.4.0
   # mysql -h 127.0.0.1 -P 4000 -u root
   # SET PASSWORD = '123456';
   # see https://hub.docker.com/r/pingcap/tidb/tags
   # or build it yourself
   # see https://github.com/pingcap/tidb
   ./impomysql taskpool ./resources/testtidb.json
   ```

4. oceanbase
   
   ```shell
   # sudo docker run -itd --name oceanbasetest -p 2881:2881 oceanbase/oceanbase-ce:4.0.0.0
   # mysql -h 127.0.0.1 -P 2881 -u root
   # SET PASSWORD = PASSWORD('123456');
   # see https://hub.docker.com/r/oceanbase/oceanbase-ce/tags
   # or build it yourself
   # see https://github.com/oceanbase/oceanbase
   ./impomysql taskpool ./resources/testoceanbase.json
   ```

## 4. Tools

### 4.1 ckstable

We assume that you have finished the **quick start** in **3.5 run task pool**.

#### intro

Some bugs are unstable. 

For a task, you can use the following command to check stable bugs and unstable bugs:

```shell
./impomysql ckstable task taskConfigPath execNum
# for example
./impomysql ckstable task ./output/mysql/task-0-config.json 10
```

We will repeat the `originalSql`/`MutatedSql` of each bug `execNum`(recommended 10) times, save the stable bugs into directory `maystable`, save the unstable bugs into directory `unstable`.

You can also use the following command to check the entire taskpool:

```shell
./impomysql ckstable taskpool taskPoolConfigPath threadNum execNum
# although we can read threadNum from config file, we think it is more flexible to specify the threadNum on the command line.
# for example
./impomysql ckstable taskpool ./resources/taskpoolconfig.json 16 10
```

Note that we use `maystable` instead of `stable`. Yes, it is very difficult to check whether a bug is stable. 

If you find some strange problems in the following chapters, first consider whether it is caused by unstable bugs.

#### example

```shell
./impomysql ckstable taskpool ./resources/taskpoolconfig.json 16 10
```

Take `./output/mysql/task0` as an example, you will see 2 new directories `maystable` and `unstable`. 

The directory `unstable` is empty, means that all bugs under `task0` are stable bugs. () 

### 4.2 sqlsim

We assume that you have finished the **quick start** in **3.5 run task pool** and **4.1 ckstable**.

#### intro

For a task, you can use the following command to simplify the sql statements of `stable` bugs:

```shell
./impomysql sqlsim task taskConfigPath
# for example
./impomysql sqlsim task ./output/mysql/task-0-config.json
```

We will try to remove each ast node in original/mutated sql statement, simplify if the implication oracle can still detect the bug.

After that, you will see a new folder `sqlsim` under `task-0` with some friendly sql statements.

You can also use the following command to simplify the entire taskpool:

```shell
./impomysql sqlsim taskpool taskPoolConfigPath threadNum
# although we can read threadNum from config file, we think it is more flexible to specify the threadNum on the command line.
# for example 
./impomysql sqlsim taskpool ./resources/taskpoolconfig.json 16
```

#### example

```shell
./impomysql sqlsim taskpool ./resources/taskpoolconfig.json 16
```

Task the mutatedSql in `task-0/maystable/bug-0-21-FixMHaving1U.json` and `task-0/sqlsim/bug-0-21-FixMHaving1U.json` as an example, you will see:

```sql
WITH `MYWITH` AS ((SELECT (0^`f5`&ADDTIME(_UTF8MB4'2017-06-19 02:05:51', _UTF8MB4'18:20:54')) AS `f1`,(`f5`+`f6`>>TIMESTAMP(_UTF8MB4'2000-06-08')) AS `f2`,(CONCAT_WS(`f4`, `f5`, `f5`)) AS `f3` FROM (SELECT `col_float_key_unsigned` AS `f4`,`col_bigint_undef_signed` AS `f5`,`col_float_undef_signed` AS `f6` FROM `table_3_utf8_2` USE INDEX (`col_bigint_key_unsigned`, `col_bigint_key_signed`)) AS `t1` HAVING 1 ORDER BY `f5`) UNION (SELECT (BINARY COS(0)|1) AS `f1`,(!1) AS `f2`,(LOWER(`f9`)) AS `f3` FROM (SELECT `col_decimal(40, 20)_key_unsigned` AS `f7`,`col_bigint_key_unsigned` AS `f8`,`col_bigint_key_signed` AS `f9` FROM `table_3_utf8_2` IGNORE INDEX (`col_decimal(40, 20)_key_unsigned`, `col_varchar(20)_key_signed`)) AS `t2` WHERE (((DATE_ADD(_UTF8MB4'16:47:10', INTERVAL 1 MONTH)) IN (SELECT `col_decimal(40, 20)_key_unsigned` FROM `table_3_utf8_2`)) OR ((ROW(`f8`,DATE_SUB(BINARY LOG2(8572968212617203413), INTERVAL 1 HOUR_SECOND)) IN (SELECT `col_bigint_key_unsigned`,`col_decimal(40, 20)_undef_unsigned` FROM `table_7_utf8_2` USE INDEX (`col_double_key_unsigned`, `col_decimal(40, 20)_key_unsigned`))) IS FALSE) OR ((`f7`) BETWEEN `f7` AND `f9`)) IS TRUE ORDER BY `f7`)) SELECT * FROM `MYWITH`;
```

changed to:

```sql
SELECT (0^`f5`&ADDTIME('2017-06-19 02:05:51', '18:20:54')) AS `f1`,(`f5`+`f6`>>TIMESTAMP('2000-06-08')) AS `f2`,(CONCAT_WS(`f4`, `f5`, `f5`)) AS `f3` FROM (SELECT `col_float_key_unsigned` AS `f4`,`col_bigint_undef_signed` AS `f5`,`col_float_undef_signed` AS `f6` FROM `table_3_utf8_undef`) AS `t1` HAVING 1;
```

### 4.3 affversion

We assume that you have finished the **quick start** in **3.5 run task pool** and **4.1 ckstable** and **4.2 sqlsim**

#### intro

You may need to verify which DBMS versions a logical bug affects.  

For a task, you can use `affversion` to verify if the bugs under sqlsim can be reproduced on the specified version of DBMS:

```shell
./impomysql affversion task taskConfigPath port version [whereVersionStatus]
# such as:
./impomysql affversion task ./output/mysql/task-0-config.json 13306 8.0.30
./impomysql affversion task ./output/mysql/task-0-config.json 13307 5.7 8.0.30@1
```

We will create a sqlite database `affversion.db` under the sibling directory of the task's path with a table:

```sqlite
CREATE TABLE IF NOT EXISTS `affversion` (`taskId` INT, `bugJsonName` TEXT, `version` TEXT, `status` INT);
CREATE INDEX IF NOT EXISTS `tv` ON `affversion` (`taskId`, `version`);
```

If a bug has already been checked, we will skip it. Specifically, we will execute the following query:

```sqlite
SELECT bugJsonName FROM `affversion` WHERE `taskId`=taskId AND `version`=version);
```

* `port`: although we can read port from config file, we think it is more flexible to specify the port on the command line.

* `taskId`: the id of the task, e.g. 0, 1, 2, ...

* `bugJsonName`: the json file name of the bug, e.g. bug-0-21-FixMHaving1U, you can use task-`taskId`/sqlsim/`bugJsonName` to read the bug.

* `version`, `status`: whether the bug can be reproduced on the specified version of DBMS.
  
   `version` can be an arbitrary non-empty string, it is recommended to use tag or commit id. 
  
  `status`: 1-yes; 0-no; -1-error.

* `whereVersionStatus`: format: version@status.

* If `whereVersionStatus` == "", we will verify each bug under task-`taskId`/sqlsim, 
  
  otherwise we will only verify these bugs:
  
  ```sqlite
  SELECT `bugJsonName` FROM `affversion`
  WHERE `taskId` = taskId AND `version` = version AND `status` = status
  ```
  

According to the reproduction status of the bug, we will insert a new record to `affversion`:

```sqlite
INSERT INTO `affversion` VALUES (taskId, bugJsonName, version, status)
```

You can also use the following command to verify the entire taskpool:

```shell
./impomysql affversion taskpool taskPoolConfigPath threadNum port version [whereVersionEQ]
# although we can read threadNum from config file, we think it is more flexible to specify the threadNum on the command line.
# such as:
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13306 8.0.30
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13307 5.7 8.0.30@1
```

Note that:

* You need to deploy the specified version of DBMS yourself.
* Old versions may crash or exception, we need to save logs for debugging. logPath: `taskPoolPath/affversion-version.log` (if version has `/`, change to `@`)
* Make sure you have done `sqlsim`.  Because some new features cannot run on the old version of DBMS, but the bug is not caused by them. 
Unfortunately, perfect simplification is almost impossible. 
If a sql cannot be executed on the old version, you'd better check it manually. ~~or just ignore it.~~

> Actually, we will verify which features in ./resources/impo.yy can not run on mysql 5.0.15 (the oldest version in mysql download page: https://downloads.mysql.com/archives/community/), and try to remove them.

#### example

Run `affversion` :

```shell
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13306 8.0.30
```

You will see a new sqlite database under  `./output/mysql`, and a table `affversion`:

```sqlite
sqlite> select * from affversion;
taskId      bugJsonName                  version     status    
----------  ---------------------------  ----------  ----------
11          bug-0-75-FixMDistinctL.json  8.0.30      1         
0           bug-0-21-FixMHaving1U.json   8.0.30      1         
6           bug-0-84-FixMHaving1U.json   8.0.30      1         
6           bug-1-91-FixMDistinctL.json  8.0.30      1         
```

It means that all bugs can be reproduced on `mysql 8.0.30`. 

Then deploy `mysql 5.7`:

```shell
sudo docker run -itd --name mysqltest2 -p 13307:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:5.7
```

Run `affversion` again:

```shell
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13307 5.7 8.0.30@1
```

See table `affversion`:

```sqlite
sqlite> select * from affversion;
taskId      bugJsonName                  version     status    
----------  ---------------------------  ----------  ----------
11          bug-0-75-FixMDistinctL.json  8.0.30      1         
0           bug-0-21-FixMHaving1U.json   8.0.30      1         
6           bug-0-84-FixMHaving1U.json   8.0.30      1         
6           bug-1-91-FixMDistinctL.json  8.0.30      1         
11          bug-0-75-FixMDistinctL.json  5.7         0         
6           bug-0-84-FixMHaving1U.json   5.7         1         
0           bug-0-21-FixMHaving1U.json   5.7         1         
6           bug-1-91-FixMDistinctL.json  5.7         0 
```

It means that some bugs cannot be reproduced on `mysql 5.7`. You can manually verify yourself.

### 4.4 dbdeployer

#### 4.4.1 affdbdeployer

In `affversion`, we need to manually deploy each version of DBMS.

Now this work can be done automatically, see https://github.com/qaqcatz/dbdeployer

With `dbdeployer`, you can use the following command to verify all versions from `newestImage `(empty means the global newest image) to `oldestImage` (epmty means the global oldest image):

```shell
./impomysql affdbdeployer dbDeployerPath dbJsonPath taskPoolConfigPath threadNum port newestImage oldestImage
# for example
# ./impomysql affdbdeployer ../dbdeployer/dbdeployer ../dbdeployer/db.json ./resources/taskpoolconfig.json 16 10001 mysql:8.0.31 ""
```

#### 4.4.2 affclassify

Classify bugs according to the versions they affect.

Specifically, for each bug, we will calculate the oldest reproducible version `o1v`,
if the bug can not be reproduced on the previous version of `o1v` (and no error), we will use `o1v` for classification.

Make sure you have done `affversion` or `affdbdeployer`, we will query the database `affversion.db`.
You also need to provide `dbdeployer`, which will tell us the order of each version.

So the command is:

```shell script
./impomysql affclassify dbDeployerPath dbJsonPath taskPoolConfigPath
# for example
./impomysql affclassify ../dbdeployer/dbdeployer ../dbdeployer/db.json ./resources/taskpoolconfig.json
```

We will create:
* `affclassify.json` in taskPoolPath. It is an array of {`o1v`, bug list}.
* directory `affclassify` in taskPoolPath. For each `o1v`, we will save the first detected bug in `affclassify`.

### 4.5 sqlsimx

`sqlsimx` is a more powerful, flexible sql simplification tool:

```shell
./impomysql sqlsimx "dml" | "ddl" inputDMLPath inputDDLPath outputPath host post username password dbname
# such as:
# ./impomysql sqlsimx dml ./dml.sql ./ddl.sql ./output.sql 127.0.0.1 13306 root 123456 TEST
# ./impomysql sqlsimx ddl ./dml.sql ./ddl.sql ./output.sql 127.0.0.1 13306 root 123456 TEST
```

You can only provide one sql statement in `inputDMLPath`!

* If you use `dml`, we will try to remove each node in your sql statement, simplify if the result does not change. 
* If you use `ddl`, we will remove unused tables, columns (only consider `CREATE TABLE` and `INSERT INTO VALUES`, may error).

Then write the simplified sql to `outputPath`.