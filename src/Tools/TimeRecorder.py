# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/10/25 16:28
# @Author  : shaocanfan
# @File    : Tools.py
# @Intro   :
import json
import time
from datetime import datetime

def record_time():
    # 记录开始时间
    start_time = datetime.now()
    time.sleep(2)
    end_time = datetime.now()
    print((end_time-start_time).total_seconds())

    print("开始时间:", start_time.strftime("%Y-%m-%d %H:%M:%S"))  # 类型：<class 'datetime.datetime'>
    # 将 datetime 对象转换为字符串
    data = {
        'current_time': start_time.isoformat()  # 使用 ISO 8601 格式
    }

    # 将数据写入 JSON 文件
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file)

    # 从 JSON 文件读取数据
    with open('data.json', 'r') as json_file:
        data_load = json.load(json_file)

    # 将字符串转换回 datetime 对象
    start_time_load = datetime.fromisoformat(data_load['current_time'])

    print("读取的时间:", start_time_load)

    # 停顿十秒
    time.sleep(2)

    # 记录结束时间
    end_time = datetime.now()

    print("结束时间:", end_time.strftime("%Y-%m-%d %H:%M:%S"))

    # 计算时间间隔
    interval = end_time - start_time_load
    print("时间间隔:", interval)

    # 将时间间隔转换为秒
    interval_seconds = interval.total_seconds()
    print("时间间隔（秒）:", interval_seconds)


record_time()