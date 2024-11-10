## MariaDB to others
1. MySQL
```
mapping 字符串匹配直接成功的个数：349
mapping 字符串匹配失败的个数：52

mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.03225806451612903(1/31)
Information Functions:0.15(3/20)
String Functions:0.11475409836065574(7/61)
Date & Time Functions:0.016129032258064516(1/62)
Geographic Functions:0.17073170731707318(14/82)
Miscellaneous Functions:0.0(0/20)
Aggregate Functions:0.0(0/17)
Control Flow Functions:0.25(1/4)
JSON Functions:0.06060606060606061(2/33)
Encryption, Hashing and Compression Functions:0.375(6/16)
No Category:0.18181818181818182(4/22)
Window Functions:0.14285714285714285(1/7)
SEQUENCE Functions:0.0(0/3)
Regular Expressions Functions:0.0(0/5)
Spider Functions:0.5(2/4)
Dynamic Columns Functions:0.875(7/8)
Vector Functions:0.3333333333333333(1/3)
Galera Functions:0.6666666666666666(2/3)
```

2. ClickHouse
```
mapping 字符串匹配直接成功的个数：267
mapping 字符串匹配失败的个数：134

mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.1935483870967742(6/31)
Information Functions:0.1(2/20)
String Functions:0.21311475409836064(13/61)
Date & Time Functions:0.0(0/62)
Geographic Functions:0.5975609756097561(49/82)
Miscellaneous Functions:0.65(13/20)
Aggregate Functions:0.11764705882352941(2/17)
Control Flow Functions:0.25(1/4)
JSON Functions:0.6060606060606061(20/33)
Encryption, Hashing and Compression Functions:0.6875(11/16)
No Category:0.2727272727272727(6/22)
Window Functions:0.14285714285714285(1/7)
SEQUENCE Functions:1.0(3/3)
Regular Expressions Functions:0.0(0/5)
Spider Functions:0.25(1/4)
Dynamic Columns Functions:0.625(5/8)
Vector Functions:0.3333333333333333(1/3)
Galera Functions:0.0(0/3)
```

3. PostgreSQL
```
mapping 字符串匹配直接成功的个数：247
mapping 字符串匹配失败的个数：154

mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.0967741935483871(3/31)
Information Functions:0.55(11/20)
String Functions:0.26229508196721313(16/61)
Date & Time Functions:0.11290322580645161(7/62)
Geographic Functions:0.8780487804878049(72/82)
Miscellaneous Functions:0.45(9/20)
Aggregate Functions:0.0(0/17)
Control Flow Functions:1.0(4/4)
JSON Functions:0.36363636363636365(12/33)
Encryption, Hashing and Compression Functions:0.6875(11/16)
No Category:0.045454545454545456(1/22)
Window Functions:0.0(0/7)
SEQUENCE Functions:0.3333333333333333(1/3)
Regular Expressions Functions:0.0(0/5)
Spider Functions:0.75(3/4)
Dynamic Columns Functions:0.125(1/8)
Vector Functions:1.0(3/3)
Galera Functions:0.0(0/3)
```

4. TiDB
```
mapping 字符串匹配直接成功的个数：280
mapping 字符串匹配失败的个数：121

mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.06451612903225806(2/31)
Information Functions:0.25(5/20)
String Functions:0.13114754098360656(8/61)
Date & Time Functions:0.04838709677419355(3/62)
Geographic Functions:0.9024390243902439(74/82)
Miscellaneous Functions:0.0(0/20)
Aggregate Functions:0.35294117647058826(6/17)
Control Flow Functions:0.0(0/4)
JSON Functions:0.09090909090909091(3/33)
Encryption, Hashing and Compression Functions:0.125(2/16)
No Category:0.2727272727272727(6/22)
Window Functions:0.14285714285714285(1/7)
SEQUENCE Functions:0.0(0/3)
Regular Expressions Functions:0.4(2/5)
Spider Functions:0.75(3/4)
Dynamic Columns Functions:0.5(4/8)
Vector Functions:0.6666666666666666(2/3)
Galera Functions:0.0(0/3)
```

5. SQLite
```
mapping 字符串匹配直接成功的个数：235
mapping 字符串匹配失败的个数：166


mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.0967741935483871(3/31)
Information Functions:0.5(10/20)
String Functions:0.26229508196721313(16/61)
Date & Time Functions:0.04838709677419355(3/62)
Geographic Functions:0.9512195121951219(78/82)
Miscellaneous Functions:0.75(15/20)
Aggregate Functions:0.47058823529411764(8/17)
Control Flow Functions:0.25(1/4)
JSON Functions:0.15151515151515152(5/33)
Encryption, Hashing and Compression Functions:0.8125(13/16)
No Category:0.22727272727272727(5/22)
Window Functions:0.14285714285714285(1/7)
SEQUENCE Functions:0.3333333333333333(1/3)
Regular Expressions Functions:0.2(1/5)
Spider Functions:0.0(0/4)
Dynamic Columns Functions:0.375(3/8)
Vector Functions:0.6666666666666666(2/3)
Galera Functions:0.3333333333333333(1/3)
```

6. MonetDB
```
mapping 字符串匹配直接成功的个数：225
mapping 字符串匹配失败的个数：176

mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.12903225806451613(4/31)
Information Functions:0.6(12/20)
String Functions:0.32786885245901637(20/61)
Date & Time Functions:0.1935483870967742(12/62)
Geographic Functions:0.7804878048780488(64/82)
Miscellaneous Functions:0.7(14/20)
Aggregate Functions:0.17647058823529413(3/17)
Control Flow Functions:0.5(2/4)
JSON Functions:0.09090909090909091(3/33)
Encryption, Hashing and Compression Functions:0.8125(13/16)
No Category:0.6818181818181818(15/22)
Window Functions:0.0(0/7)
SEQUENCE Functions:0.0(0/3)
Regular Expressions Functions:0.0(0/5)
Spider Functions:1.0(4/4)
Dynamic Columns Functions:0.75(6/8)
Vector Functions:0.6666666666666666(2/3)
Galera Functions:0.6666666666666666(2/3)
```

7. DuckDB
```
mapping 字符串匹配直接成功的个数：261
mapping 字符串匹配失败的个数：152

mapping 字符串匹配失败的各个类别占比：
Numeric Functions:0.08823529411764706(3/34)
Information Functions:0.19047619047619047(4/21)
String Functions:0.3387096774193548(21/62)
Date & Time Functions:0.0(0/65)
Geographic Functions:0.8433734939759037(70/83)
Miscellaneous Functions:0.7(14/20)
Aggregate Functions:0.15789473684210525(3/19)
Control Flow Functions:0.0(0/4)
JSON Functions:0.5151515151515151(17/33)
Encryption, Hashing and Compression Functions:0.23529411764705882(4/17)
No Category:0.3181818181818182(7/22)
Window Functions:0.0(0/7)
SEQUENCE Functions:0.0(0/3)
Regular Expressions Functions:0.2(1/5)
Spider Functions:0.75(3/4)
Dynamic Columns Functions:0.375(3/8)
Vector Functions:0.6666666666666666(2/3)
Galera Functions:0.0(0/3)
```



## SQLite to others
1. MySQL
```
mapping 字符串匹配直接成功的个数：129
mapping 字符串匹配失败的个数：12


mapping 字符串匹配失败的各个类别占比：
Built-in Aggregate Functions:0.0(0/10)
Date And Time Functions:0.0(0/7)
JSON Functions:0.19230769230769232(5/26)
Built-In Mathematical SQL Functions:0.13333333333333333(4/30)
Built-In Window Functions:0.0(0/11)
Built-In Scalar SQL Functions:0.05263157894736842(3/57)
```

2. ClickHouse
```
mapping 字符串匹配直接成功的个数：90
mapping 字符串匹配失败的个数：51


mapping 字符串匹配失败的各个类别占比：
Built-in Aggregate Functions:0.2(2/10)
Date And Time Functions:0.2857142857142857(2/7)
JSON Functions:0.9230769230769231(24/26)
Built-In Mathematical SQL Functions:0.16666666666666666(5/30)
Built-In Window Functions:0.36363636363636365(4/11)
Built-In Scalar SQL Functions:0.24561403508771928(14/57)

```

3. PostgreSQL
```
mapping 字符串匹配直接成功的个数：118
mapping 字符串匹配失败的个数：23


mapping 字符串匹配失败的各个类别占比：
Built-in Aggregate Functions:0.0(0/10)
Date And Time Functions:0.14285714285714285(1/7)
JSON Functions:0.3076923076923077(8/26)
Built-In Mathematical SQL Functions:0.0(0/30)
Built-In Window Functions:0.0(0/11)
Built-In Scalar SQL Functions:0.24561403508771928(14/57)

```

4. TiDB
```
mapping 字符串匹配直接成功的个数：123
mapping 字符串匹配失败的个数：18


mapping 字符串匹配失败的各个类别占比：
Built-in Aggregate Functions:0.0(0/10)
Date And Time Functions:0.0(0/7)
JSON Functions:0.07692307692307693(2/26)
Built-In Mathematical SQL Functions:0.16666666666666666(5/30)
Built-In Window Functions:0.0(0/11)
Built-In Scalar SQL Functions:0.19298245614035087(11/57)
```

5. MariaDB
```
mapping 字符串匹配直接成功的个数：112
mapping 字符串匹配失败的个数：29


mapping 字符串匹配失败的各个类别占比：
Built-in Aggregate Functions:0.1(1/10)
Date And Time Functions:0.0(0/7)
JSON Functions:0.15384615384615385(4/26)
Built-In Mathematical SQL Functions:0.26666666666666666(8/30)
Built-In Window Functions:0.36363636363636365(4/11)
Built-In Scalar SQL Functions:0.21052631578947367(12/57)

```

6. MonetDB
```
mapping 字符串匹配直接成功的个数：70
mapping 字符串匹配失败的个数：71


mapping 字符串匹配失败的各个类别占比：
Built-in Aggregate Functions:0.1(1/10)
Date And Time Functions:0.7142857142857143(5/7)
JSON Functions:0.9615384615384616(25/26)
Built-In Mathematical SQL Functions:0.16666666666666666(5/30)
Built-In Window Functions:0.18181818181818182(2/11)
Built-In Scalar SQL Functions:0.5789473684210527(33/57)
```

7. DuckDB
```
mapping 字符串匹配直接成功的个数：70
mapping 字符串匹配失败的个数：71

mapping 字符串匹配失败的各个类别占比：
Built-in Aggregate Functions:0.2(2/10)
Date And Time Functions:0.8571428571428571(6/7)
JSON Functions:1.0(26/26)
Built-In Mathematical SQL Functions:0.23333333333333334(7/30)
Built-In Window Functions:0.0(0/11)
Built-In Scalar SQL Functions:0.5263157894736842(30/57)

```


## Postgres to others
1. MySQL
```
mapping 字符串匹配直接成功的个数：435
mapping 字符串匹配失败的个数：200

mapping 字符串匹配失败的各个类别占比：
Comparison Functions and Operators:0.0(0/2)
String Functions and Operators:0.07272727272727272(4/55)
Mathematical Functions and Operators:0.2641509433962264(14/53)
Binary String Functions and Operators:0.0(0/26)
Bit String Functions and Operators:0.0(0/9)
Data Type Formatting Functions:0.0(0/4)
Date divide Time Functions and Operators:0.0(0/27)
Enum Support Functions:0.6666666666666666(2/3)
Geometric Functions and Operators:0.45454545454545453(10/22)
Network Address Functions and Operators:0.21428571428571427(3/14)
Text Search Functions and Operators:0.6666666666666666(18/27)
JSON Functions and Operators:0.10714285714285714(6/56)
Sequence Manipulation Functions:0.25(1/4)
Array Functions and Operators:0.42105263157894735(8/19)
Range divide Multirange Functions and Operators:0.5(5/10)
Aggregate Functions:0.27450980392156865(14/51)
Window Functions:0.0(0/11)
Merge Support Functions:0.0(0/1)
Set Returning Functions:0.0(0/2)
System Information Functions and Operators:0.5259259259259259(71/135)
System Administration Functions:0.42424242424242425(42/99)
Trigger Functions:0.6666666666666666(2/3)
Event Trigger Functions:0.0(0/2)
```

2. ClickHouse

```
mapping 字符串匹配直接成功的个数：301
mapping 字符串匹配失败的个数：334

mapping 字符串匹配失败的各个类别占比：
Comparison Functions and Operators:0.0(0/2)
String Functions and Operators:0.2545454545454545(14/55)
Mathematical Functions and Operators:0.2830188679245283(15/53)
Binary String Functions and Operators:0.3076923076923077(8/26)
Bit String Functions and Operators:0.6666666666666666(6/9)
Data Type Formatting Functions:0.0(0/4)
Date divide Time Functions and Operators:0.0(0/27)
Enum Support Functions:0.6666666666666666(2/3)
Geometric Functions and Operators:0.7272727272727273(16/22)
Network Address Functions and Operators:0.8571428571428571(12/14)
Text Search Functions and Operators:0.7037037037037037(19/27)
JSON Functions and Operators:0.625(35/56)
Sequence Manipulation Functions:0.75(3/4)
Array Functions and Operators:0.15789473684210525(3/19)
Range divide Multirange Functions and Operators:0.7(7/10)
Aggregate Functions:0.5098039215686274(26/51)
Window Functions:0.2727272727272727(3/11)
Merge Support Functions:1.0(1/1)
Set Returning Functions:0.0(0/2)
System Information Functions and Operators:0.5925925925925926(80/135)
System Administration Functions:0.797979797979798(79/99)
Trigger Functions:1.0(3/3)
Event Trigger Functions:1.0(2/2)
```
3. PostgreSQL
```
1

```

4. TiDB
```
mapping 字符串匹配直接成功的个数：379
mapping 字符串匹配失败的个数：256

mapping 字符串匹配失败的各个类别占比：
Comparison Functions and Operators:1.0(2/2)
String Functions and Operators:0.14545454545454545(8/55)
Mathematical Functions and Operators:0.41509433962264153(22/53)
Binary String Functions and Operators:0.11538461538461539(3/26)
Bit String Functions and Operators:0.4444444444444444(4/9)
Data Type Formatting Functions:0.0(0/4)
Date divide Time Functions and Operators:0.18518518518518517(5/27)
Enum Support Functions:0.6666666666666666(2/3)
Geometric Functions and Operators:0.7272727272727273(16/22)
Network Address Functions and Operators:0.42857142857142855(6/14)
Text Search Functions and Operators:0.5185185185185185(14/27)
JSON Functions and Operators:0.17857142857142858(10/56)
Sequence Manipulation Functions:0.0(0/4)
Array Functions and Operators:0.8947368421052632(17/19)
Range divide Multirange Functions and Operators:0.9(9/10)
Aggregate Functions:0.43137254901960786(22/51)
Window Functions:0.0(0/11)
Merge Support Functions:0.0(0/1)
Set Returning Functions:1.0(2/2)
System Information Functions and Operators:0.362962962962963(49/135)
System Administration Functions:0.6262626262626263(62/99)
Trigger Functions:1.0(3/3)
Event Trigger Functions:0.0(0/2)
```

5. MariaDB
```

```

6. MonetDB
```
mapping 字符串匹配直接成功的个数：157
mapping 字符串匹配失败的个数：478

mapping 字符串匹配失败的各个类别占比：
Comparison Functions and Operators:0.5(1/2)
String Functions and Operators:0.6(33/55)
Mathematical Functions and Operators:0.3584905660377358(19/53)
Binary String Functions and Operators:0.5769230769230769(15/26)
Bit String Functions and Operators:0.8888888888888888(8/9)
Data Type Formatting Functions:0.75(3/4)
Date divide Time Functions and Operators:0.6666666666666666(18/27)
Enum Support Functions:1.0(3/3)
Geometric Functions and Operators:0.9545454545454546(21/22)
Network Address Functions and Operators:0.5(7/14)
Text Search Functions and Operators:0.9259259259259259(25/27)
JSON Functions and Operators:0.8214285714285714(46/56)
Sequence Manipulation Functions:0.25(1/4)
Array Functions and Operators:0.9473684210526315(18/19)
Range divide Multirange Functions and Operators:0.9(9/10)
Aggregate Functions:0.4117647058823529(21/51)
Window Functions:0.18181818181818182(2/11)
Merge Support Functions:1.0(1/1)
Set Returning Functions:0.5(1/2)
System Information Functions and Operators:0.9555555555555556(129/135)
System Administration Functions:0.9292929292929293(92/99)
Trigger Functions:1.0(3/3)
Event Trigger Functions:1.0(2/2)
```

7. DuckDB
```
mapping 字符串匹配直接成功的个数：333
mapping 字符串匹配失败的个数：302


mapping 字符串匹配失败的各个类别占比：
Comparison Functions and Operators:1.0(2/2)
String Functions and Operators:0.34545454545454546(19/55)
Mathematical Functions and Operators:0.3584905660377358(19/53)
Binary String Functions and Operators:0.38461538461538464(10/26)
Bit String Functions and Operators:0.3333333333333333(3/9)
Data Type Formatting Functions:0.75(3/4)
Date divide Time Functions and Operators:0.4074074074074074(11/27)
Enum Support Functions:0.6666666666666666(2/3)
Geometric Functions and Operators:0.9090909090909091(20/22)
Network Address Functions and Operators:0.9285714285714286(13/14)
Text Search Functions and Operators:0.7777777777777778(21/27)
JSON Functions and Operators:0.8571428571428571(48/56)
Sequence Manipulation Functions:0.75(3/4)
Array Functions and Operators:0.7894736842105263(15/19)
Range divide Multirange Functions and Operators:0.1(1/10)
Aggregate Functions:0.0784313725490196(4/51)
Window Functions:0.0(0/11)
Merge Support Functions:0.0(0/1)
Set Returning Functions:0.0(0/2)
System Information Functions and Operators:0.37777777777777777(51/135)
System Administration Functions:0.5252525252525253(52/99)
Trigger Functions:1.0(3/3)
Event Trigger Functions:1.0(2/2)
```


## MySQL to others
1. MySQL
```
mapping 字符串匹配直接成功的个数：607
mapping 字符串匹配失败的个数：299


mapping 字符串匹配失败的各个类别占比：
Built-In Functions:0.32524271844660196(268/824)
Loadable Functions:0.38271604938271603(31/81)
String Functions:0.0(0/1)

```

2. ClickHouse

```
mapping 字符串匹配直接成功的个数：507
mapping 字符串匹配失败的个数：399


mapping 字符串匹配失败的各个类别占比：
Built-In Functions:0.42354368932038833(349/824)
Loadable Functions:0.6049382716049383(49/81)
String Functions:1.0(1/1)
```
3. PostgreSQL
```
1

```

4. TiDB
```

```

5. MariaDB
```

```

6. MonetDB
```
mapping 字符串匹配直接成功的个数：249
mapping 字符串匹配失败的个数：657


mapping 字符串匹配失败的各个类别占比：
Built-In Functions:0.7111650485436893(586/824)
Loadable Functions:0.8641975308641975(70/81)
String Functions:1.0(1/1)
```

7. DuckDB
```
apping 字符串匹配直接成功的个数：253
mapping 字符串匹配失败的个数：653


mapping 字符串匹配失败的各个类别占比：
Built-In Functions:0.7075242718446602(583/824)
Loadable Functions:0.8518518518518519(69/81)
String Functions:1.0(1/1)
```


## TiDB to others
1. MySQL
```
1
```

2. ClickHouse

```
mapping 字符串匹配直接成功的个数：206
mapping 字符串匹配失败的个数：71


mapping 字符串匹配失败的各个类别占比：
Aggregate Functions:0.36363636363636365(4/11)
Information Functions:0.07692307692307693(1/13)
JSON Functions:0.5(16/32)
Bit Functions:0.0(0/1)
Cast Functions:0.3333333333333333(1/3)
Locking Functions:0.8(4/5)
Mathematical Functions:0.13333333333333333(4/30)
Date and Time Functions:0.01694915254237288(1/59)
Miscellaneous Functions:0.3888888888888889(7/18)
Sequence Functions:0.75(3/4)
String Functions:0.2413793103448276(14/58)
TiDB Specific Functions:0.4666666666666667(7/15)
Window Functions:0.36363636363636365(4/11)
Encryption and Compression Functions:0.3076923076923077(4/13)
Flow Control Functions:0.25(1/4)
```
3. PostgreSQL
```
1

```

4. TiDB
```
mapping 字符串匹配直接成功的个数：607
mapping 字符串匹配失败的个数：299


mapping 字符串匹配失败的各个类别占比：
Built-In Functions:0.32524271844660196(268/824)
Loadable Functions:0.38271604938271603(31/81)
String Functions:0.0(0/1)
```

5. MariaDB
```

```

6. MonetDB
```
mapping 字符串匹配直接成功的个数：124
mapping 字符串匹配失败的个数：153


mapping 字符串匹配失败的各个类别占比：
Aggregate Functions:0.36363636363636365(4/11)
Information Functions:0.9230769230769231(12/13)
JSON Functions:0.3125(10/32)
Bit Functions:1.0(1/1)
Cast Functions:0.6666666666666666(2/3)
Locking Functions:1.0(5/5)
Mathematical Functions:0.23333333333333334(7/30)
Date and Time Functions:0.6949152542372882(41/59)
Miscellaneous Functions:0.9444444444444444(17/18)
Sequence Functions:0.75(3/4)
String Functions:0.39655172413793105(23/58)
TiDB Specific Functions:0.9333333333333333(14/15)
Window Functions:0.09090909090909091(1/11)
Encryption and Compression Functions:0.8461538461538461(11/13)
Flow Control Functions:0.5(2/4)

```

7. DuckDB
```
mapping 字符串匹配直接成功的个数：113
mapping 字符串匹配失败的个数：164


mapping 字符串匹配失败的各个类别占比：
Aggregate Functions:0.36363636363636365(4/11)
Information Functions:0.5384615384615384(7/13)
JSON Functions:0.96875(31/32)
Bit Functions:1.0(1/1)
Cast Functions:1.0(3/3)
Locking Functions:0.8(4/5)
Mathematical Functions:0.2(6/30)
Date and Time Functions:0.5423728813559322(32/59)
Miscellaneous Functions:0.6666666666666666(12/18)
Sequence Functions:0.5(2/4)
String Functions:0.603448275862069(35/58)
TiDB Specific Functions:0.9333333333333333(14/15)
Window Functions:0.0(0/11)
Encryption and Compression Functions:0.9230769230769231(12/13)
Flow Control Functions:0.25(1/4)

```


## MonetDB to others
1. MySQL
```
1
```

2. ClickHouse

```
mapping 字符串匹配直接成功的个数：215
mapping 字符串匹配失败的个数：104


mapping 字符串匹配失败的各个类别占比：
Logical Functions:0.0(0/4)
Character String Functions:0.3880597014925373(26/67)
Comparison Functions:0.42857142857142855(6/14)
Binary String Functions:1.0(2/2)
Date Time Functions:0.31746031746031744(20/63)
Cast Conversion Functions:0.0(0/2)
INET Functions:0.7692307692307693(10/13)
Mathematics Functions:0.25925925925925924(14/54)
JSON Functions:0.4117647058823529(7/17)
URL Functions:0.375(6/16)
UUID Functions:0.0(0/2)
Aggregate Functions:0.16129032258064516(5/31)
Window Functions:0.25806451612903225(8/31)
Generate Series Functions:0.0(0/3)
```
3. PostgreSQL
```
1

```

4. TiDB
```

```

5. MariaDB
```

```

6. MonetDB
```


```

7. DuckDB
```
mapping 字符串匹配直接成功的个数：174
mapping 字符串匹配失败的个数：145


mapping 字符串匹配失败的各个类别占比：
Logical Functions:0.5(2/4)
Character String Functions:0.373134328358209(25/67)
Comparison Functions:0.7142857142857143(10/14)
Binary String Functions:0.0(0/2)
Date Time Functions:0.36507936507936506(23/63)
Cast Conversion Functions:1.0(2/2)
INET Functions:1.0(13/13)
Mathematics Functions:0.2962962962962963(16/54)
JSON Functions:0.9411764705882353(16/17)
URL Functions:1.0(16/16)
UUID Functions:0.5(1/2)
Aggregate Functions:0.3870967741935484(12/31)
Window Functions:0.2903225806451613(9/31)
Generate Series Functions:0.0(0/3)

```


## TiDB to others
1. MySQL
```
1
```

2. ClickHouse

```
mapping 字符串匹配直接成功的个数：206
mapping 字符串匹配失败的个数：71


mapping 字符串匹配失败的各个类别占比：
Aggregate Functions:0.36363636363636365(4/11)
Information Functions:0.07692307692307693(1/13)
JSON Functions:0.5(16/32)
Bit Functions:0.0(0/1)
Cast Functions:0.3333333333333333(1/3)
Locking Functions:0.8(4/5)
Mathematical Functions:0.13333333333333333(4/30)
Date and Time Functions:0.01694915254237288(1/59)
Miscellaneous Functions:0.3888888888888889(7/18)
Sequence Functions:0.75(3/4)
String Functions:0.2413793103448276(14/58)
TiDB Specific Functions:0.4666666666666667(7/15)
Window Functions:0.36363636363636365(4/11)
Encryption and Compression Functions:0.3076923076923077(4/13)
Flow Control Functions:0.25(1/4)
```
3. PostgreSQL
```
1

```

4. TiDB
```
mapping 字符串匹配直接成功的个数：607
mapping 字符串匹配失败的个数：299


mapping 字符串匹配失败的各个类别占比：
Built-In Functions:0.32524271844660196(268/824)
Loadable Functions:0.38271604938271603(31/81)
String Functions:0.0(0/1)
```

5. MariaDB
```

```

6. MonetDB
```
mapping 字符串匹配直接成功的个数：124
mapping 字符串匹配失败的个数：153


mapping 字符串匹配失败的各个类别占比：
Aggregate Functions:0.36363636363636365(4/11)
Information Functions:0.9230769230769231(12/13)
JSON Functions:0.3125(10/32)
Bit Functions:1.0(1/1)
Cast Functions:0.6666666666666666(2/3)
Locking Functions:1.0(5/5)
Mathematical Functions:0.23333333333333334(7/30)
Date and Time Functions:0.6949152542372882(41/59)
Miscellaneous Functions:0.9444444444444444(17/18)
Sequence Functions:0.75(3/4)
String Functions:0.39655172413793105(23/58)
TiDB Specific Functions:0.9333333333333333(14/15)
Window Functions:0.09090909090909091(1/11)
Encryption and Compression Functions:0.8461538461538461(11/13)
Flow Control Functions:0.5(2/4)

```

7. DuckDB
```
mapping 字符串匹配直接成功的个数：113
mapping 字符串匹配失败的个数：164


mapping 字符串匹配失败的各个类别占比：
Aggregate Functions:0.36363636363636365(4/11)
Information Functions:0.5384615384615384(7/13)
JSON Functions:0.96875(31/32)
Bit Functions:1.0(1/1)
Cast Functions:1.0(3/3)
Locking Functions:0.8(4/5)
Mathematical Functions:0.2(6/30)
Date and Time Functions:0.5423728813559322(32/59)
Miscellaneous Functions:0.6666666666666666(12/18)
Sequence Functions:0.5(2/4)
String Functions:0.603448275862069(35/58)
TiDB Specific Functions:0.9333333333333333(14/15)
Window Functions:0.0(0/11)
Encryption and Compression Functions:0.9230769230769231(12/13)
Flow Control Functions:0.25(1/4)

```


## DuckDB to others
1. MySQL
```
1
```

2. ClickHouse

```
mapping 字符串匹配直接成功的个数：416
mapping 字符串匹配失败的个数：199


mapping 字符串匹配失败的各个类别占比：
Aggregate Functions:0.41975308641975306(34/81)
Bitstring Functions:0.6153846153846154(8/13)
Blob Functions:0.4(2/5)
Date Functions:0.4074074074074074(11/27)
Date Part Functions:0.038461538461538464(1/26)
Enum Functions:0.6(3/5)
Interval Functions:0.1875(3/16)
Lambda Functions:0.5454545454545454(6/11)
List Functions:0.2159090909090909(19/88)
Map Functions:0.5(6/12)
Numeric Functions:0.25(14/56)
Regular Expressions:0.125(1/8)
Struct Functions:0.25(2/8)
Text Functions:0.2358490566037736(25/106)
Time Functions:0.4(4/10)
Timestamp Functions:0.38461538461538464(15/39)
Timestamp with Time Zone Functions:0.34146341463414637(14/41)
Union Functions:1.0(4/4)
Utility Functions:0.37142857142857144(13/35)
Window Functions:0.5333333333333333(8/15)
Array Functions:0.6666666666666666(6/9)
```
3. PostgreSQL
```
1

```

4. TiDB
```

```

5. MariaDB
```

```

6. MonetDB
```


```

7. DuckDB
```


```

|     | <100 | 100-200 | 200-300 | 300-400 | >400  |     |
| --- | ---- | ------- | ------- | ------- | ----- | --- |
| 语法  | 0.96 | 0.97    | 0.94    | 0.90    | <0.82 |     |
| 语义  | 0.91 | 0.      |         |         |       |     |



[100, 200]
单次转换(未错误迭代)执行成功/总样本：0.000 (0/1)
错误迭代/总样本：1.000 (1/1)
错误迭代执行成功/错误迭代：1.000 (1/1)
执行成功/总样本：1.000 (1/1)
--------------------------------------------------
执行结果一致/执行成功：0.000 (0/1)
执行结果一致/总样本：0.000 (0/1)
--------------------------------------------------
[200, 300]
单次转换(未错误迭代)执行成功/总样本：0.190 (19/100)
错误迭代/总样本：0.810 (81/100)
错误迭代执行成功/错误迭代：0.963 (78/81)
执行成功/总样本：0.970 (97/100)
--------------------------------------------------
执行结果一致/执行成功：0.000 (0/97)
执行结果一致/总样本：0.000 (0/100)
--------------------------------------------------




[200, 300]
单次转换(未错误迭代)执行成功/总样本：0.812 (26/32)
错误迭代/总样本：0.188 (6/32)
错误迭代执行成功/错误迭代：1.000 (6/6)
执行成功/总样本：1.000 (32/32)
--------------------------------------------------
执行结果一致/执行成功：0.750 (24/32)
执行结果一致/总样本：0.750 (24/32)
--------------------------------------------------


[400, 2500]
单次转换(未错误迭代)执行成功/总样本：0.748 (332/444)
错误迭代/总样本：0.252 (112/444)
错误迭代执行成功/错误迭代：0.393 (44/112)
执行成功/总样本：0.847 (376/444)
--------------------------------------------------
执行结果一致/执行成功：0.513 (193/376)
执行结果一致/总样本：0.435 (193/444)



```
{
'a_db': {'index': 1, 'Feature': ['FOUND_ROWS()\n']}, 
'b_db': {'Feature': ['SQL_CALC_FOUND_ROWS and FOUND_ROWS()'], 'Explanation': 'In MySQL, the combination of the SQL_CALC_FOUND_ROWS modifier and the FOUND_ROWS() function serves a similar purpose to the FOUND_ROWS() function in MariaDB. Both features allow you to determine the total number of rows that would have been returned by a query without a LIMIT clause, although it is important to note that these features are deprecated in MySQL and users are encouraged to use separate queries with COUNT(*) instead.', 'index': -1}
}


{
"a_db": {"index": 1, "Feature": ["FOUND_ROWS()\n"]}, 
"b_db": {"Feature": ["FOUND_ROWS()"], "Explanation": "....", "index": 7}
}



{'a_db': {'index': 388, 'Feature': ['sys.extract_schema_from_file_name(path)\n']}, 'b_db': {'Feature': ['sys.extract_schema_from_file_name'], 'Explanation': 'The similar feature in MySQL is not directly mentioned in the retrieved context. However, both MariaDB and MySQL support JSON functions like JSON_EXTRACT, which allow manipulation and retrieval of data from JSON documents in a structured manner. The specific feature in MariaDB that extracts schema from file names might not have a direct equivalent in MySQL as indicated by the lack of related mentions in the provided context.', 'index': -1}}

{"a_db": {"index": 388, "Feature": ["sys.extract_schema_from_file_name(path)\n"]}, "b_db": {"Feature": ["SCHEMA()"], "Explanation": "...", "index": 470}}

```

