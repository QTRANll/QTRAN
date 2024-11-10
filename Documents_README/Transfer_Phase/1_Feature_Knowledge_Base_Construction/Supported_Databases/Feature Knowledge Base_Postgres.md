# Functions(finished)

* functions和operators是混合在一起，分类别进行展示的。
## Functions文档相关链接
英文版本：
[PostgreSQL: Documentation: 17: Chapter 9. Functions and Operators](https://www.postgresql.org/docs/current/functions.html)
### Fucntions目录解释

## 爬取Functions
### 数据结构

### 爬取过程
1. 先获取所有的html(function和operator用同一套)
* 需要手动获取的如下
	* [PostgreSQL: Documentation: 17: 9.1. Logical Operators](https://www.postgresql.org/docs/current/functions-logical.html) 
	* [PostgreSQL: Documentation: 17: 9.7. Pattern Matching](https://www.postgresql.org/docs/current/functions-matching.html)
	* [PostgreSQL: Documentation: 17: 9.14. UUID Functions](https://www.postgresql.org/docs/current/functions-uuid.html)
* 下面的格式比较特殊
	* [PostgreSQL: Documentation: 17: 9.15. XML Functions](https://www.postgresql.org/docs/current/functions-xml.html)
2. 所有的functions都会在对应的表格中列出：表格有以下两种情况，区别在于内部是否含有p；包含p则是情况1和2图，认为只看第一列，不包含p则是情况3图，读取所有的列（一般为2列）
![[Pasted image 20241012171251.png|400]]
![[Pasted image 20241012183934.png]]
![[Pasted image 20241012171229.png|400]]

3. functions和operators是混合在一起存储在表格中的，这里一起统一处理。下面是所有表格`<div class="table">`的可能的thead的名称

``` Python
[  
  [  
    'Operator',  
    'Description'  
  ],  
  [  
    'Predicate',  
    'Description',  
    'Example(s)'  
  ],  
  [  
    'Function',  
    'Description',  
    'Example(s)'  
  ],  
  [  
    'Operator',  
    'Description',  
    'Example(s)'  
  ],  
  [  
    'Function/Operator',  
    'Description',  
    'Example(s)'  
  ],  
  [  
    'Function signature',  
    'Description',  
    'Example(s)'  
  ],  
  [  
    'Operator/Method',  
    'Description',  
    'Example(s)'  
  ],  
  [  
    'Predicate/Value',  
    'Description',  
    'Example(s)'  
  ],  
  [  
    'Function',  
    'Description'  
  ],  
  [  
    'Function',  
    'Description',  
    'Example Usage'  
  ]  
]
```
4. 概括上面table的共同特点
* 都包含“Description”
* 第一个列名包含了表格内feature类型的信息
	* 只包含Operator：Operator
	* 只包含Function：Function，Function signature
	* 均包含：Function/Operator，Operator/Method，Predicate（可以不包含），Predicate/Value（可以不包含）
	* 不做考虑的情况：Atom，Quantifier，Constraint，Escape，Option，SQL standard，Pattern，Modifier，Expression，Name，Flag
*  对于列名的不同情况做以下处理
	* 只包含Operator：全认为是operator
	* 只包含Function：全认为是function
	* 均包含：包含(和)的认为是function，其余的认为是operator
	* 不做考虑的情况：跳过即可
5. 表格的详细信息以下面的样式组织
* 其中第一行，关于feature：以`<p class="func_signature">`格式存储，以class为识别关键点，个数不止一个
* 第二行紧接着，关于desceription，以`<p>`格式存储，个数不止一个，class读取出来应该是none
* 第三行紧接着（不是必有项），关于examples，以`<p>`格式存储，class读取出来应该是none，text文本一般包含 →（少部分无返回值的函数不包含，则会被归类到description中） ，只要包含则认为是example，个数不止一个
![[Pasted image 20241012164359.png|500]]

# Operators(finished)

functions和operators是混合在一起，分类别进行展示的。
## Operators文档相关链接
英文版本：
[PostgreSQL: Documentation: 17: Chapter 9. Functions and Operators](https://www.postgresql.org/docs/current/functions.html)
### Opeartors目录解释

## 爬取Operators
### 数据结构

### 爬取过程
1. 先获取所有的html(function和operator用同一套)
2. 所有的opearators都会在对应的表格中列出



# SQL Statements(unfinished)
## SQL Statements相关链接

英文版本：

中文版本：
暂无
## SQL Statements元素解释
## 爬取SQL Documents

### 数据结构

### 爬取过程

















