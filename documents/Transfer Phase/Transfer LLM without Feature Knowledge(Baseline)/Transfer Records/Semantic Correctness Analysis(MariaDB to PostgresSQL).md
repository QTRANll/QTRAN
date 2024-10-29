以长度区间在1-240的101条数据的转换结果为基础，分析语义准确性，并总结error-iteration保证语法准确性的过程原理。
101条，error_iteration=True，sqls_type="simple"，FewShot=True ，length_range = [1,240)

## error-iteration
llm基于返回的error message对sql语句进行修改，其修改手段可总结大致如下：
1. target db中不存在相对应的feature或功能：将feature替换成其他可执行的feature，一般这种被替换的列都是常量列（该列所有数据均相同）。
* 函数：如COERCIBILITY('d')替换成COALESCE('d', NULL)，两者语义无关。
* 符号：如取反符号“~”在postgres中不支持整数以外的数据，取反符号出现频率很高；“~”常被替换成NOT，符号-，*（-1），或者直接删除

2. target db中存在相应的feature或功能：将feature替换成相应的feature，并且修改参数值的类型来满足相应feature的语法
* 函数：如"index"=6，LCASE(1)替换成LOWER(CAST(1 AS TEXT))，这是由于postgres中LOWER的参数不能为intger
* 符号：直接替换
* 等价表达式替换：如"index"=13，LOG10(3)替换成(LOG(3) / LOG(10))
## 不同DB执行结果偏差
1. 类型：返回的执行结果的类型不一样，但结果相近
* "index"=1：一个为-122，一个为Decimal('-122')
* ”index"=2：一个为，一个为datetime.timedelta(days=34, seconds=82799)，一个为datetime.datetime(2023, 7, 22, 4, 26, 40, tzinfo=datetime.timezone.utc)
* “ index"=24：同为整数的取反~操作，结果也会不一致