# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 11:35 上午
# @Author  : zhengjiawei
# @FileName: test_api.py
# @Software: PyCharm

import requests
import json
# response = requests.post(url='http://10.30.89.124:5000/deal_request', data={'row_key': 'hou-ding-zi_86368310'})
data = json.dumps({'sentence': '我喜欢你'})
response = requests.get(url='http://127.0.0.1:8000/api/query/features/term', data=data)
response_dict = response.json()  # 获取返回的dict，对应6节中response.json()的表
print(response_dict)