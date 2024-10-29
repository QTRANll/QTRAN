[![Build Status](https://github.com/sqlancer/sqlancer/workflows/ci/badge.svg)](https://github.com/sqlancer/sqlancer/actions)
[![Twitter](https://img.shields.io/twitter/follow/sqlancer_dbms?style=social)](https://twitter.com/sqlancer_dbms)
# SQLancer
SQLancer，全称为Synthesized Query Lancer，该工具是一款针对数据库管理系统DBMS的自动化安全测试工具。该工具可以帮助广大研究人员轻松识别应用程序实现中的逻辑漏洞。我们这里所指的逻辑漏洞，即能够导致DBMS获取错误结果集的安全漏洞（比如说忽略数据记录等等）。

SQLancer的工作分为以下两个阶段:
1. 数据库生成：此阶段的目标是创建一个填充有数据的数据库，并向DBMS输入测试用例以尝试识别和检测不一致数据库状态。随后，该工具将会创建一个随机表，并随机选择SQL语句来生成、修改和删除数据。除此之外，该工具还会使用其他类型的语句（如创建索引和视图以及设置DBMS特定选项的语句）来测试目标DBMS。
2. 测试：这个阶段的目标是针对生成的数据库检测逻辑错误。请参见下面的"测试方法"部分。**News:我们现在支持差异化查询计划(DQP)oracle。请参见下面的"测试方法"部分。**
# Getting Started

Requirements:
* Java 11 or above
* [Maven](https://maven.apache.org/) (`Ubuntu安装：sudo apt install maven`)
* The DBMS that you want to test (embedded DBMSs such as DuckDB, H2, and SQLite do not require a setup)

广大研究人员可以使用下列命令将SQLancer项目源码克隆至本地，然后创建一个JAR，并启动SQLancer来测试SQLite，此过程使用的是非优化引用引擎结构（NoREC：Non-optimizing Reference Engine Construction ）：

```
git clone https://github.com/sqlancer/sqlancer
cd sqlancer
mvn package -DskipTests
cd target
java -jar sqlancer-*.jar --num-threads 4 sqlite3 --oracle NoREC
```

如果执行之后，工具每5秒打印一次处理信息，则说明该工具按预期正常工作。SQLancer可能会找出SQLite中的漏洞，在报告漏洞信息之前，请确保处理信息仍在打印。**我们可以按下CTRL + C组合键手动停止SQLancer的运行。** 如果SQLancer没有找出漏洞，那么它将会一直运行下去。我们可以使用`--num-trie`来控制SQLancer在找到多少漏洞之后停止运行。除此之外，我们也可以使用`--timeout-seconds`来指定SQLancer允许执行的最大超时。

如果不带参数启动SQLancer，工具则会输出所有可用的选项和命令。请注意，所有DBMS测试实现都支持的通用选项(例如，`——num-threads`)需要在要测试的DBMS的名称之前(例如，`sqlite3`)。只支持特定DBMS的选项(例如，SQLite3的`--test-rtree`)，或者每个测试实现提供不同值的选项(例如:`--oracle NoREC`)需要在DBMS名称之后。


# Testing Approaches

| Approach                                             | Description                                                                                                                                                       |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pivoted Query Synthesis (PQS)                        | PQS是我们设计并实现的第一个技术。它随机选择一行(称为枢轴行)，并为其生成一个保证能获取该行的查询。如果结果集中不包含该行，则表示检测到错误。详细描述[在这里](https://arxiv.org/abs/2001.04174)。PQS是最强大的技术，但也比其他两种技术需要更多的实现工作。它目前没有维护。        |
| Non-optimizing Reference Engine Construction (NoREC) | NoREC旨在发现优化错误。它被描述[在这里](https://www.manuelrigger.at/preprints/NoREC.pdf)。它将可能由DBMS优化的查询转换为几乎不适用任何优化的查询，并比较两个结果集。结果集之间的不匹配表明DBMS中存在错误。                             |
| Ternary Logic Partitioning (TLP)                     | TLP将一个查询划分为三个分区查询，将它们的结果进行合并，并与原始查询的结果集进行比较。两个结果集的不匹配表明DBMS中存在错误。与NoREC和PQS相比，它可以检测聚合函数等高级features中的错误。                                                           |
| Cardinality Estimation Restriction Testing (CERT)    | CERT 旨在通过意外的估计基数(表示返回行的估计数量)来发现性能问题。它被描述[在这里](https://arxiv.org/abs/2306.00355)。它将查询派生为更严格的查询，其估计基数应该不超过原始查询的基数。违反这一点表示可能存在性能问题。CERT 支持 TiDB、CockroachDB 和 MySQL。 |
| Differential Query Plans (DQP)                       | DQP旨在通过检查同一查询在不同的DBMSs的查询计划执行是否一致来发现数据库系统中的逻辑错误。它被描述[在这里](https://bajinsheng.github.io/assets/pdf/dqp_sigmod24.pdf)。DQP支持MySQL、MariaDB和TiDB。                      |

# Generation Approaches
| Approach                  | Description                                                                                                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Random Generation         | 随机生成是SQLancer中默认的测试用例生成方法。首先，生成随机表。然后根据表的模式随机生成查询。                                                                                                                                         |
| Query Plan Guidance (QPG) | QPG是一种由查询计划覆盖指导的测试用例生成方法。给定一个数据库状态，在数据库状态上随机生成的查询没有观察到新的唯一查询计划之后，我们对其进行变异，目的是覆盖更多唯一的查询计划，以暴露更多DBMSs的逻辑。这种方法可以通过选项`——qpg-enabl`启用，现在支持SQLite、CockroachDB、TiDB和Materialize的TLP和NoREC oracle。 |

Please find the `.bib` entries [here](docs/PAPERS.md).

# Supported DBMS

由于各自DBMS使用的SQL方言差异很大，因此需要针对要测试的不同DBMS采用单独的实现方式。

| DBMS                         | Status      | Expression Generation        | Description                                                                                                                                                                                     |
| ---------------------------- | ----------- | ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SQLite                       | Working     | Untyped                      | This implementation is currently affected by a significant performance regression that still needs to be investigated                                                                           |
| MySQL                        | Working     | Untyped                      | Running this implementation likely uncovers additional, unreported bugs.                                                                                                                        |
| PostgreSQL                   | Working     | Typed                        |                                                                                                                                                                                                 |
| Citus (PostgreSQL Extension) | Working     | Typed                        | This implementation extends the PostgreSQL implementation of SQLancer, and was contributed by the Citus team.                                                                                   |
| MariaDB                      | Preliminary | Untyped                      | The implementation of this DBMS is very preliminary, since we stopped extending it after all but one of our bug reports were addressed. Running it likely uncovers additional, unreported bugs. |
| CockroachDB                  | Working     | Typed                        |                                                                                                                                                                                                 |
| TiDB                         | Working     | Untyped                      |                                                                                                                                                                                                 |
| DuckDB                       | Working     | Untyped, Generic             |                                                                                                                                                                                                 |
| ClickHouse                   | Preliminary | Untyped, Generic             | Implementing the different table engines was not convenient, which is why only a very preliminary implementation exists.                                                                        |
| TDEngine                     | Removed     | Untyped                      | We removed the TDEngine implementation since all but one of our bug reports were still unaddressed five months after we reported them.                                                          |
| OceanBase                    | Working     | Untyped                      |                                                                                                                                                                                                 |
| YugabyteDB                   | Working     | Typed (YSQL), Untyped (YCQL) | YSQL implementation based on Postgres code. YCQL implementation is primitive for now and uses Cassandra JDBC driver as a proxy interface.                                                       |
| Databend                     | Working     | Typed                        |                                                                                                                                                                                                 |
| QuestDB                      | Working     | Untyped, Generic             | The implementation of QuestDB is still WIP, current version covers very basic data types, operations and SQL keywords.                                                                          |
| CnosDB                       | Working     | Typed                        | The implementation of CnosDB currently uses Restful API.                                                                                                                                        |
| Materialize                  | Working     | Typed                        |                                                                                                                                                                                                 |
| Apache Doris                 | Preliminary | Typed                        | This is a preliminary implementation, which only contains the common logic of Doris. We have found some errors through it, and hope to improve it in the future.                                |
| Presto                       | Preliminary | Typed                        | This is a preliminary implementation, only basic types supported.                                                                                                                               |
| DataFusion                   | Preliminary | Typed                        | Only basic SQL features are supported.                                                                                                                                                          |


# Using SQLancer

## Logs

SQLancer将日志存储在` target/logs`子目录中。默认情况下，选项`——log-each-select`是启用的，这将导致发送到DBMS的每个SQL语句都被记录。对应的文件名后缀为`-cur.log`。此外，如果SQLancer检测到逻辑错误，它会创建一个扩展名为`.log`的文件，在该文件中记录重现错误的语句。

## Reducing a Bug

在发现错误之后，在报告错误之前生成一个最小的测试用例是很有用的，这可以节省DBMS开发人员的时间和精力。对于许多测试用例，[C-Reduce](https://embed.cs.utah.edu/creduce/)做得很好。
## Found Bugs

如果您在报告SQLancer发现的bug时提到它，我们将不胜感激。我们也很想知道您是否正在使用SQLancer来查找错误，或者您是否已经扩展它来测试另一个DBMS(如果您不打算将它贡献给这个项目)。SQLancer已经在广泛使用的DBMS中发现了400多个错误，这些错误列在[这里](https://www.manuelrigger.at/dbms-bugs/)。

# Community

我们已经创建了一个[Slack工作空间](https://join.slack.com/t/sqlancer/shared_invite/zt-eozrcao4-ieG29w1LNaBDMF7OB_~ACg)来讨论SQLancer和DBMS测试。SQLancer的官方Twitter账号是[@sqlancer_dbms](https://twitter.com/sqlancer_dbms)。
# FAQ

## 我在最新版本的DBMS上运行SQLancer。是否期望SQLancer打印许多AssertionErrors?

In many cases, SQLancer does not support the latest version of a DBMS. You can check the [`.github/workflows/main.yml`](https://github.com/sqlancer/sqlancer/blob/master/.github/workflows/main.yml) file to determine which version we use in our CI tests, which corresponds to the currently supported version of that DBMS. SQLancer should print only an `AssertionError` and produce a corresponding log file, if it has identified a bug. To upgrade SQLancer to support a new DBMS version, either two options are advisable: (1) the generators can be updated to no longer generate certain patterns that might cause errors (e.g., which might be the case if a keyword or option is no longer supported) or (2) the newly-appearing errors can be added as [expected errors](https://github.com/sqlancer/sqlancer/blob/354d591cfcd37fa1de85ec77ec933d5d975e947a/src/sqlancer/common/query/ExpectedErrors.java) so that SQLancer ignores them when they appear (e.g., this is useful if some error-inducing patterns cannot easily be avoided).

Another reason for many failures on a supported version could be that error messages are printed in a non-English locale (which would then be visible in the stack trace). In such a case, try setting the DBMS' locale to English (e.g., see the [PostgreSQL homepage](https://www.postgresql.org/docs/current/locale.html)).

在许多情况下，SQLancer不支持最新版本的DBMS。您可以检查[' .github/workflows/main.yml '](https://github.com/sqlancer/sqlancer/blob/master/.github/workflows/main.yml)文件，以确定我们在CI测试中使用的版本，该版本对应于该DBMS的当前支持版本。如果SQLancer发现了一个bug，它应该只打印一个AssertionError，并生成一个相应的日志文件。要升级SQLancer以支持新的DBMS版本，建议采用以下两种方法:(1)generators可以更新不再生成特定的模式,可能会导致错误(例如,它可能是如果一个关键词或选项不再支持)或(2)新出现的错误可以当作预期错误进行添加(https://github.com/sqlancer/sqlancer/blob/354d591cfcd37fa1de85ec77ec933d5d975e947a/src/sqlancer/common/query/ExpectedErrors.java), SQLancer忽略他们出现(例如,这是有用的一些误差导致的模式不容易避免)。

在受支持的版本上出现许多失败的另一个原因可能是错误消息以非英语语言环境打印(这将在堆栈跟踪中可见)。在这种情况下，尝试将DBMS的语言环境设置为英语(例如，参见[PostgreSQL主页](https://www.postgresql.org/docs/current/locale.html))。
## 当启动SQLancer时，我得到一个错误，如database 'test' does not exist。如何运行SQLancer而不出现此错误?

对于某些dbms, SQLancer期望存在一个数据库“test”，然后将其用作要连接的初始数据库。如果你还没有创建这样的数据库，你可以使用一个命令，如' CREATE database test '来创建这个数据库(例如，参见[PostgreSQL文档](https://www.postgresql.org/docs/current/sql-createdatabase.html))。

# Additional Documentation
* [[SQLancer_CONTRIBUTING]]
* [[SQLancer_PAPERS]]

# Releases

Official release are available on:
* [GitHub](https://github.com/sqlancer/sqlancer/releases)
* [Maven Central](https://search.maven.org/artifact/com.sqlancer/sqlancer)
* [DockerHub](https://hub.docker.com/r/mrigger/sqlancer)

# Additional Resources

* A talk on Ternary Logic Partitioning (TLP) and SQLancer is available on [YouTube](https://www.youtube.com/watch?v=Np46NQ6lqP8).
* An (older) Pivoted Query Synthesis (PQS) talk is available on [YouTube](https://www.youtube.com/watch?v=yzENTaWe7qg).
* PingCAP has implemented PQS, NoREC, and TLP in a tool called [go-sqlancer](https://github.com/chaos-mesh/go-sqlancer).
* More information on our DBMS testing efforts and the bugs we found is available [here](https://www.manuelrigger.at/dbms-bugs/).
