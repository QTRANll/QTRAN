# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/9/15 22:23
# @Author  : shaocanfan
# @File    : load_data_temp.py
# @Intro   :
from src.TransferLLM.TransferLLM import load_data, init_data
load_data("output1", "mysql", 1, 800, True, 200)
init_data("output1", "mysql", 1, 800, True, 200)
load_data("output2", "mysql", 1, 800, True, 200)
init_data("output2", "mysql", 1, 800, True, 200)