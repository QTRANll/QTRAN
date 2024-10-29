## 已爬取数据集
* 涉及的变异策略：TLP,noREC
* 涉及的DB：mysql(TLP)，tidb(TLP)，oceanbase(TLP,noREC)，postgres(TLP,noREC)，sqlite(TLP,noREC)，cockroachdb(TLP,noREC)
![[Pasted image 20240808202555.png]]
## TLP
### 原理
| Ternary Logic Partitioning (TLP) | TLP将一个查询划分为三个分区查询，将它们的结果进行合并，并与原始查询的结果集进行比较。两个结果集的不匹配表明DBMS中存在错误。与NoREC和PQS相比，它可以检测聚合函数等高级features中的错误。 |
| -------------------------------- | ------------------------------------------------------------------------------------------------------- |
![[4e03fdeb1c3c08d4be964161450ff14.png]]
例子：蓝色的句子分割成了后面三个句子，然后把后面三个结果联合起来和蓝色句子结果应该一致。然后这分割的三个句子一般是随机生成一个谓语p然后 p is true ;p is false ;p is null三种。

### SQLancer中的具体实现
#### mysql(TLP)
只有where

#### tidb(TLP)
有where，having，base（不知道啥意思）
#### oceanbase
有where，base
#### postgres
where，having，base，aggregate

#### sqlite
where，having，base，aggregate,groupby,distinct


#### cockroachdb
where，having，base，aggregate,groupby,distinct




## noREC
### 原理
| Non-optimizing Reference Engine Construction (NoREC) | NoREC旨在发现优化错误。它被描述[在这里](https://www.manuelrigger.at/preprints/NoREC.pdf)。它将可能由DBMS优化的查询转换为几乎不适用任何优化的查询，并比较两个结果集。结果集之间的不匹配表明DBMS中存在错误。 |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
