# impomysql_Pinolo

[![Go Reference](https://pkg.go.dev/badge/github.com/qaqcatz/impomysql.svg)](https://pkg.go.dev/github.com/qaqcatz/impomysql)    

基于Implication Oracle检测mysql的逻辑错误。

也支持DBMS兼容mysql语法，如mariadb, tidb, oceanbase。

**注意'impomysql'是我们原来的名字，现在你也可以叫它PINOLO。我们可能会在将来创建一个新的存储库



## 1. What is logical bug

下面的bug报告就是一个例子:

https://bugs.mysql.com/bug.php?id=108937

理论上，sql1的结果 ⊆ sql2的结果:

```sql
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING f1 != 0; -- sql1
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING 1; -- sql2
```

因为`HAVING 1`在sql2中总是为真，但`HAVING f1 != 0`在sql1中可能是假的。

但是，将`HAVING f1 != 0 `更改为`HAVING 1 `后，日期值发生了变化，这是一个逻辑错误:


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

在上述的例子中：
```sql
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING f1 != 0; -- sql1
SELECT c1-DATE_SUB('2008-05-25', INTERVAL 1 HOUR_MINUTE) AS f1 FROM t HAVING 1; -- sql2
```

我们将`HAVING f1 != 0`改为`HAVING 1`。

理论上，sql1的谓词→sql2的谓词，sql1的结果 ⊆ sql2的结果。

如果实际结果不满足这种关系，我们认为存在逻辑错误。

您可以查看我们的论文了解更多细节:

```shell
@inproceedings{hao2023pinolo,
  title={Pinolo: Detecting Logical Bugs in Database Management Systems with Approximate Query Synthesis},
  author={Hao, Zongyin and Huang, Quanfeng and Wang, Chengpeng and Wang, Jianfeng and Zhang, Yushan and Wu, Rongxin and Zhang, Charles},
  booktitle={2023 USENIX Annual Technical Conference (USENIX ATC 23)},
  pages={345--358},
  year={2023}
}
```

你也可以查看源代码:

* mutation/doc.go

* mutation/stage1/doc.go

* mutation/stage2/doc.go

* mutation/stage2/mutatevisitor.go

* resources/impo.yy

## 3. How to use

### 3.1 build

建议使用“golang 1.16.2”([如何安装golang 1.16.2](https://github.com/qaqcatz/impomysql/blob/main/documents/installgo.md)) [[Ponolo_installgo]]。

```shell
git clone --depth=1 https://github.com/qaqcatz/impomysql.git
cd impomysql
go build
```

执行`git clone --depth=1 https://github.com/qaqcatz/impomysql.git`时遇到如下报错：
```
fatal: unable to access 'https://github.com/qaqcatz/impomysql.git/': Failed to connect to github.com port 443: Connection timed out
```
对应解决方法参考如下链接：
[【Github问题解决】解决Github：fatal:unable to access ‘https://github.com/.../.git‘:Could not resolve host:git_unable to access github](https://blog.csdn.net/m0_72594605/article/details/132559545)


执行`go build`之前需要安装GCC：
[Go和C混合编程新手注意事项：解决常见错误_cgo: c compiler "gcc" not found: exec: "gcc": exec](https://blog.csdn.net/liuyangqi11/article/details/131720766)

执行`go build`时遇到如下报错：
```
go: github.com/go-sql-driver/mysql@v1.6.0: Get "https://proxy.golang.org/github.com/go-sql-driver/mysql/@v/v1.6.0.mod": dial tcp 172.217.160.81:443: connect: connection refused

go: github.com/go-sql-driver/mysql@v1.6.0: Get "https://proxy.golang.org/github.com/go-sql-driver/mysql/@v/v1.6.0.mod": dial tcp 142.251.42.241:443: i/o timeout
```
对应解决方法参考如下链接：
https://blog.csdn.net/qq_47664976/article/details/122548097

可以使用模块缓存，使用Go模块缓存来下载所需的模块。依次运行以下命令。
在goland的终端输入：
```
go get github.com/go-sql-driver/mysql
```
在输入后也许会报这样的错误：
```
go get: module github.com/go-sql-driver/mysql: Get "https://proxy.golang.org/github.com/go-sql-driver/mysql/@v/list": dial tcp 142.251.42.241:443: connect
ex: A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because conn
ected host has failed to respond.
```

这是因为无法对外网进行访问，可以通过输入以下命令进入代理网站进行访问。
```
go env -w GOPROXY=https://goproxy.cn,direct
```
然后在输入上述命令就可以下载所需的模块:
```
go get github.com/go-sql-driver/mysql
```
最后再次执行`go build`就不会报错了。



**下面我们将把`imomysql`的路径称为`${IMPOHOME}`**

现在您将看到一个可执行文件( an executable file)  `${IMPOHOME}/ imomysql`。

### 3.2 start your DBMS

##### 重要：WSL，Hyper-V，Ubuntu以及Docker的安装[[WSL，Hyper-V，Ubuntu以及Docker的安装]]

例如，你可以用docker启动mysql:
```shell
sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30
```

您也可以自己编译和安装DBMS。

### 3.3 run task
我们将一次DBMS test视为一项`任务`。
#### quick start

我们假设您已经执行了`sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30`命令。

```shell
cd ${IMPOHOME}
./impomysql task ./resources/taskconfig.json
```

如果一切正常，终端中将没有任何内容，您将得到一个新目录`${IMPOHOME}/output/mysql/task-1`，其结构如下:

```shell
${IMPOHOME}/output/mysql/task-1
  |-- bugs
     |-- bug-0-0-FixMHaving1U.log
     |-- bug-0-0-FixMHaving1U.json
  |-- result.json
  |-- task.log
```

您将在`${IMPOHOME}/output/mysql/task-1`中看到一个名为`bugs`的目录，以及位于`bugs`中的两个名为`bug-0-0-FixMHaving1U.log`和`bug-0-0-FixMHaving1U.Json`的文件。这是我们检测到的逻辑错误。您可以先自己看一下这些文件，我们将在下面的文本中解释input和output的细节。


#### input

指令：

```shell
impomysql task <task configuration json file>
```

您只需要提供一个配置文件（configuration file）。我们将取`${IMPOHOME}/resources/taskconfig.Json`为例:

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

| option                                           | description                                                                                                                        |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| `outputPath`, `dbms`, `taskId`                   | 我们将结果保存在`outputPath`/`dbms`/task-`taskId`(` taskId`>= 0)中。<br>我们将删除旧目录并创建一个新目录。<br>如果您想提供一个相对路径，请记住，该路径是相对于您运行命令的目录的，而不是这个配置文件的路径。 |
| `host`, `port`, `username`, `password`, `dbname` | 我们将使用dsn `username`: `password` @tcp(`host`: `port`)/`dbname`创建一个数据库连接器，并初始化数据库` dbname`。                                          |
| `seed`                                           | 随机种子。如果seed <= 0，我们将使用当前时间。                                                                                                        |
| `ddlPath`                                        | 负责创建数据的Sql文件。<br>见`${IMPOHOME}/resources/ddl.sql`为例。                                                                               |
| `dmlPath`                                        | 负责查询数据的Sql文件。<br>我们只关注在你的`dmlPath`中的`SELECT`语句，这意味着我们会忽略一些你的sqls，如`EXPLAIN`，`PREPARE`…<br>见`${IMPOHOME}/resources/dml.sql`为例。      |

#### output

| file                                    | description                                                                                                           |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| bug-`bugId`-`sqlId`-`mutationName`.log  | 保存突变名称、原始sql、原始结果、突变的sql、突变的结果，以及原始结果和我们期望的突变结果之间的关系(`IsUpper`)。`[IsUpper] true`是指变异后的结果应该 ⊆ 原结果。                     |
| bug-`bugId`-`sqlId`-`mutationName`.json | bug-`bugId`-`sqlId`-`mutationName`.log 的Json格式                                                                        |
| `task.log`                              | 任务日志文件，从中可以获得任务进度和错误消息。                                                                                               |
| `result.json`                           | 如果任务成功执行，我们将创建一个结果文件，从中您可以获得任务的开始时间(`startTime`)、结束时间(`endTime`)以及我们检测到的逻辑错误数量(`impoBugsNum`)。<br>剩下的字段用于我们的调试，请忽略它们! |



### 3.4 run task with go-randgen

一个 `task`可以在[go-randgen](https://github.com/pingcap/go-randgen)的帮助下自动生成`ddlPath` and `dmlPath`，你需要先构建它。

#### build go-randgen

```shell
git clone https://github.com/pingcap/go-randgen.git
cd go-randgen
go get -u github.com/jteeuwen/go-bindata/...
# make sure you have added GOPATH/bin to your environment variable PATH
make all
```
现在你会看到一个可执行文件`go-randgen`，把它复制到`${IMPOHOME}/resources`。

```
cp go-randgen ~/impomysql/resources
```

#### quick start

我们假设您已经执行了`sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30`。

```shell
cd ${IMPOHOME}
./impomysql task ./resources/taskrdgenconfig.json
```

如果一切正常，终端中将没有任何内容，您将得到一个新目录`${IMPOHOME}/output/mysql/task-1`，其结构如下:

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

除了任务的标准输出(即bugs、task.log、result.json)之外，您还将看到两个sql文件`output.data.sql`, `output.rand.sql`。这是`go-randgen`自动生成的`ddlPath` 和`dmlPath`。


#### input


以 `${IMPOHOME}/resources/taskrdgenconfig.json`为例。我们删除了`ddlPath` 和 `dmlPath`，添加了`randGenPath`, `zzPath`, `yyPath`, `queriesNum`, `needDML`:

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

| option             | description                                                                                                                                                                                                                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `randGenPath`      | go-randgen可执行文件的路径                                                                                                                                                                                                                                                                                     |
| `zzPath`, `yyPath` | `go-randgen`将根据`zzPath`生成一个ddl sql文件`output.data.sql`，并根据`yyPath`生成一个dml sql文件`output.rand.sql`。我们在`${IMPOHOME}/resources`中提供了一个默认的zz文件`impo.zz.lua`和一个默认的yy文件`impo.yy`。建议使用这些默认文件。我们实际执行以下命令:`cd outputPath/dbms/task-taskId && randGenPath gentest -Z zzPath -Y yyPath -Q queriesNum --seed seed -B` |
| `queriesNum`       | `output.rand.sql`中的sqls数目                                                                                                                                                                                                                                                                              |
| `needDML`          | 如果`needDML`为假，我们将在`task` 结束后删除`output.rand.sql`。建议将此值设置为false，因为`output.rand.sql`通常非常大(10000个sql大约10MB)。                                                                                                                                                                                               |


注意，如果你同时使用了(non empty) `rdGenPath` 和（`ddlPath`,`dmlPath`），我们将run `task` with `go-randgen`，并将`ddlPath`设置为`outputPath/dbms/task-taskId/output.data.sql`，将`dmlPath`设置为`outputPath/dbms/task-taskId/output.rand.sql`。

#### output
除了 `bugs`, `task.log`, `result.json`，您还会看到output.data.sql`, `output.rand.sql`。

当然，如果你将`needDML` 设置为false，我们将删除`output.rand.sql`。



### 3.5 run task pool

`taskpool`可以连续并行运行任务。确保您可以使用[go-randgen](https://github.com/pingcap/go-randgen)运行task。
#### quick start

我们假设您已经执行了`sudo docker run -itd --name mysqltest -p 13306:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:8.0.30`。

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


如果一切正常，您将得到一个新目录 `${IMPOHOME}/output/mysql`，其结构如下:

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

`taskpool`将生成一系列任务配置，并根据这些配置运行相应的任务。我们将在下面的文本中解释输入和输出的细节。
#### input

以 `${IMPOHOME}/resources/taskpoolconfig.json` 为例:

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

| option      | description                                             |
| ----------- | ------------------------------------------------------- |
| `threadNum` | The number of threads                                   |
| `maxTasks`  | Maximum number of tasks, <= 0 means no limit.           |
| `maxTimeS`  | Maximum time(second), <=0 means no limit.               |
| `dbPrefix`  | 对于每个线程，我们将创建一个数据库连接器，每个连接器的dbname是`dbPrefix`+thread id。 |
| `seed`      | The seed of each task is `seed`+task id.                |

注意:

* 我们将设置`needDML`为false。
* 建议将`queriesNum`设置为较大的值(>=10000，一个`queriesNum`=10000的任务大约需要5~10分钟)，否则会得到很多任务目录。

#### output

| option                    | description                                                                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| task-`taskId`-config.json | The configuration file of task-`taskId`.                                                                                                    |
| `taskpool.log`            | Taskpool log file, from which you can get taskpool progress and error message.                                                              |
| `result.json`             | 如果任务池执行成功，我们将创建一个结果文件，从中您可以获得任务池的开始时间(' startTime ')，结束时间(`endTime`)，我们检测到的逻辑错误的数量(`bugsNum`)及其taskId(`bugTaskIds`)。<br>剩下的字段用于我们的调试，请忽略它们! |


#### test dbms

我们为mysql, mariadb, tidb, oceanbase提供了默认配置文件，您可以按照这些配置文件来测试您自己的数据库。

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

我们假设您已经完成了**3.5 run task pool**的**quick start** **。

#### intro

有些bug是不稳定的。

对于一个任务，可以使用如下命令查看稳定bug和不稳定bug:

```shell
# command foramt
./impomysql ckstable task taskConfigPath execNum

# for example
./impomysql ckstable task ./output/mysql/task-0-config.json 10
```


我们将每个bug的`originalSql`/ `MutatedSql`重复`execNum`(建议10次)，将稳定的bug保存到`maystable`目录，将不稳定的bug保存到`unstable`目录。

也可以使用如下命令查看整个任务池:

```shell
./impomysql ckstable taskpool taskPoolConfigPath threadNum execNum
# although we can read threadNum from config file, we think it is more flexible to specify the threadNum on the command line.

# for example
./impomysql ckstable taskpool ./resources/taskpoolconfig.json 16 10
```

注意我们用的是`maystable`而不是`stable`。是的，要检查一个bug是否稳定是非常困难的。

如果你在接下来的章节中发现了一些奇怪的问题，首先要考虑它是否是由不稳定的bug引起的。

#### example

```shell
./impomysql ckstable taskpool ./resources/taskpoolconfig.json 16 10
```

以`./output/mysql/task0`为例，你会看到两个新目录`maystable`和`unstable`。

目录`unstable`为空，意味着`task0`下的所有bug都是稳定的bug。

### 4.2 sqlsim

我们假设您已经完成了**3.5 run task pool** 的**quick start** ** 和 **4.1 ckstable**。

#### intro

对于一个任务，您可以使用以下命令来简化`stable`bug的sql语句:


```shell
./impomysql sqlsim task taskConfigPath
# for example
./impomysql sqlsim task ./output/mysql/task-0-config.json
```


我们将尝试删除原始/变异sql语句中的每一个ast节点，如果 the implication oracle仍然可以检测到错误则进行简化。

之后，您将在`task-0`下看到一个新文件夹`sqlsim`，其中包含一些友好的sql语句。

您也可以使用以下命令来简化整个任务池:

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

以`task-0/maystable/bug-0-21-FixMHaving1U.json`和`task-0/sqlsim/bug-0-21-FixMHaving1U.json`中的变异sql为例子，你会看到:

```sql
WITH `MYWITH` AS ((SELECT (0^`f5`&ADDTIME(_UTF8MB4'2017-06-19 02:05:51', _UTF8MB4'18:20:54')) AS `f1`,(`f5`+`f6`>>TIMESTAMP(_UTF8MB4'2000-06-08')) AS `f2`,(CONCAT_WS(`f4`, `f5`, `f5`)) AS `f3` FROM (SELECT `col_float_key_unsigned` AS `f4`,`col_bigint_undef_signed` AS `f5`,`col_float_undef_signed` AS `f6` FROM `table_3_utf8_2` USE INDEX (`col_bigint_key_unsigned`, `col_bigint_key_signed`)) AS `t1` HAVING 1 ORDER BY `f5`) UNION (SELECT (BINARY COS(0)|1) AS `f1`,(!1) AS `f2`,(LOWER(`f9`)) AS `f3` FROM (SELECT `col_decimal(40, 20)_key_unsigned` AS `f7`,`col_bigint_key_unsigned` AS `f8`,`col_bigint_key_signed` AS `f9` FROM `table_3_utf8_2` IGNORE INDEX (`col_decimal(40, 20)_key_unsigned`, `col_varchar(20)_key_signed`)) AS `t2` WHERE (((DATE_ADD(_UTF8MB4'16:47:10', INTERVAL 1 MONTH)) IN (SELECT `col_decimal(40, 20)_key_unsigned` FROM `table_3_utf8_2`)) OR ((ROW(`f8`,DATE_SUB(BINARY LOG2(8572968212617203413), INTERVAL 1 HOUR_SECOND)) IN (SELECT `col_bigint_key_unsigned`,`col_decimal(40, 20)_undef_unsigned` FROM `table_7_utf8_2` USE INDEX (`col_double_key_unsigned`, `col_decimal(40, 20)_key_unsigned`))) IS FALSE) OR ((`f7`) BETWEEN `f7` AND `f9`)) IS TRUE ORDER BY `f7`)) SELECT * FROM `MYWITH`;
```

变为：

```sql
SELECT (0^`f5`&ADDTIME('2017-06-19 02:05:51', '18:20:54')) AS `f1`,(`f5`+`f6`>>TIMESTAMP('2000-06-08')) AS `f2`,(CONCAT_WS(`f4`, `f5`, `f5`)) AS `f3` FROM (SELECT `col_float_key_unsigned` AS `f4`,`col_bigint_undef_signed` AS `f5`,`col_float_undef_signed` AS `f6` FROM `table_3_utf8_undef`) AS `t1` HAVING 1;
```

### 4.3 affversion

我们假设您已经完成了**3.5 run task pool** 的**quick start** ** 和 **4.1 ckstable**和**4.2 sqlsim**。
#### intro

您可能需要验证一个逻辑错误影响的是哪个DBMS版本。

对于一个任务，你可以使用`affversion`来验证：sqlsim下的错误是否可以在指定版本的DBMS上重现:

```shell
./impomysql affversion task taskConfigPath port version [whereVersionStatus]
# such as:
./impomysql affversion task ./output/mysql/task-0-config.json 13306 8.0.30
./impomysql affversion task ./output/mysql/task-0-config.json 13307 5.7 8.0.30@1
```

我们将在任务路径的兄弟目录下创建一个名为`affversion.db` 的sqlite数据库，并创建一个表:

```sqlite
CREATE TABLE IF NOT EXISTS `affversion` (`taskId` INT, `bugJsonName` TEXT, `version` TEXT, `status` INT);
CREATE INDEX IF NOT EXISTS `tv` ON `affversion` (`taskId`, `version`);
```

如果一个bug已经被检查过了，我们将跳过它。具体来说，我们将执行以下查询:

```sqlite
SELECT bugJsonName FROM `affversion` WHERE `taskId`=taskId AND `version`=version);
```

* `port`:虽然我们可以从配置文件中读取端口，但我们认为在命令行中指定端口更灵活。

* `taskId`:任务的id，例如0,1,2，…

* `bugJsonName`: bug的json文件名，例如bug-0-21-FixMHaving1U，你可以使用task-`taskId`/sqlsim/`bugJsonName`读取bug。

* `version`，`status`:该错误是否可以在指定版本的DBMS上重现。`version`可以是任意的非空字符串，建议使用标签或提交id。`status`: 1-yes; 0-no; -1-error.

* `whereVersionStatus`: format: version@status.

* 如果`whereVersionStatus`== ""，我们将验证在task-`taskId`/sqlsim下的每个bug;否则我们将只验证这些错误:
  
  ```sqlite
  SELECT `bugJsonName` FROM `affversion`
  WHERE `taskId` = taskId AND `version` = version AND `status` = status
  ```
根据bug的 reproduction status ，我们将在`affversion`中插入一条新记录:

```sqlite
INSERT INTO `affversion` VALUES (taskId, bugJsonName, version, status)
```

也可以使用以下命令验证整个任务池:

```shell
./impomysql affversion taskpool taskPoolConfigPath threadNum port version [whereVersionEQ]
# although we can read threadNum from config file, we think it is more flexible to specify the threadNum on the command line.
# such as:
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13306 8.0.30
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13307 5.7 8.0.30@1
```

注意:

* 您需要自己部署指定版本的DBMS。
* 旧版本可能会崩溃或异常，我们需要保存日志以便调试。logPath: `taskPoolPath/affversion-version.log` '(如果version有`/ `，更改为`@`)
* 确保您已经执行了`sqlsim`。因为一些新特性不能在旧版本的DBMS上运行，但错误不是由它们引起的。
不幸的是，完美的简化几乎是不可能的。
如果sql不能在旧版本上执行，您最好手动检查它。~~或者忽略它~~


>实际上，我们将验证./resources/impo.yy中的哪些特性无法在mysql 5.0.15 (mysql最旧版本下载页面:https://downloads.mysql.com/archives/community/中最老版本)上运行，并尝试删除。


#### example

运行 `affversion` :

```shell
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13306 8.0.30
```

您将在`./output/mysql`下看到一个新的sqlite数据库，和一个`affversion`表:

```sqlite
sqlite> select * from affversion;
taskId      bugJsonName                  version     status    
----------  ---------------------------  ----------  ----------
11          bug-0-75-FixMDistinctL.json  8.0.30      1         
0           bug-0-21-FixMHaving1U.json   8.0.30      1         
6           bug-0-84-FixMHaving1U.json   8.0.30      1         
6           bug-1-91-FixMDistinctL.json  8.0.30      1         
```


这意味着所有的bug都可以在`mysql 8.0.30`上重现。

然后部署`mysql 5.7`:

```shell
sudo docker run -itd --name mysqltest2 -p 13307:3306 -e MYSQL_ROOT_PASSWORD=123456 mysql:5.7
```

再次运行 `affversion` :

```shell
./impomysql affversion taskpool ./resources/taskpoolconfig.json 16 13307 5.7 8.0.30@1
```

查看表 `affversion`:

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

这意味着一些错误不能在`mysql 5.7`上重现。您可以手动验证自己。


### 4.4 dbdeployer

#### 4.4.1 affdbdeployer

在`affversion`中，我们需要手动部署每个版本的DBMS。

现在这项工作可以自动完成，参见 https://github.com/qaqcatz/dbdeployer

使用`dbdeployer`，您可以使用以下命令来验证从`newestImage`(空表示全局最新映像)到` oldestImage`(空表示全局最旧映像)的所有版本:

```shell
./impomysql affdbdeployer dbDeployerPath dbJsonPath taskPoolConfigPath threadNum port newestImage oldestImage
# for example
# ./impomysql affdbdeployer ../dbdeployer/dbdeployer ../dbdeployer/db.json ./resources/taskpoolconfig.json 16 10001 mysql:8.0.31 ""
```

#### 4.4.2 affclassify

根据影响的版本对bug进行分类。

具体来说，对于每个bug，我们将计算最旧的可复制版本`o1v`，
如果错误不能在以前版本的`o1v`上重现(并且没有错误)，我们将使用`o1v`进行分类。

确保你已经执行了`affversion`或`affdbdeployer`，我们将查询数据库`affversion.db`。
您还需要提供`dbdeployer`，它将告诉我们每个版本的顺序。

所以命令是:

```shell script
./impomysql affclassify dbDeployerPath dbJsonPath taskPoolConfigPath
# for example
./impomysql affclassify ../dbdeployer/dbdeployer ../dbdeployer/db.json ./resources/taskpoolconfig.json
```

我们将创造:
*  taskPoolPath中的`affclassify.josn` 。它是 {`o1v`, bug list}的一个数组。
* taskPoolPath中的`affclassified`目录。对于每个`o1v`，我们将第一个检测到的bug保存在`affclassified`中。

### 4.5 sqlsimx

`sqlsimx`是一个更强大、更灵活的SQL简化工具:
```shell
./impomysql sqlsimx "dml" | "ddl" inputDMLPath inputDDLPath outputPath host post username password dbname
# such as:
# ./impomysql sqlsimx dml ./dml.sql ./ddl.sql ./output.sql 127.0.0.1 13306 root 123456 TEST
# ./impomysql sqlsimx ddl ./dml.sql ./ddl.sql ./output.sql 127.0.0.1 13306 root 123456 TEST
```

您只能在`inputDMLPath`中提供一条sql语句!

* 如果您使用`dml`，我们将尝试删除sql语句中的每个节点，如果结果没有变化，我们将进行简化。
* 如果你使用`ddl`，我们将删除未使用的表，列(只考虑`CREATE TABLE`和`INSERT INTO VALUES`，可能会出错)。

然后将简化的sql写入`outputPath`。