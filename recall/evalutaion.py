# -*- coding: utf-8 -*-
# @Time    : 2022/3/24 9:18 下午
# @Author  : zhengjiawei
# @FileName: evalutaion.py
# @Software: PyCharm
import pandas as pd

# 读取 test数据集
# 对于每一个样本
# search_token 进行recall
# 样本中的id 是否在recall的id列表中

# 常用的评价标准：

# 第一类是线上评测，比如通过点击率、网站流量、A/B test等判断

# 第二类是线下评测。评测标准很多
# hit Rate
data_test = pd.read_csv('test_search_data.csv')
