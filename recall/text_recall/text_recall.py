# -*- coding: utf-8 -*-
# @Time    : 2022/2/25 4:47 下午
# @Author  : zhengjiawei
# @FileName: text_recall.py
# @Software: PyCharm

from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="http://10.30.89.124:9200/")  # , http_auth=('abc','dataanalysis')
print(es)

query_json = {
    "query": {
        "bool": {
            "should": [{
                "match": {
                    "content": "自然语言处理"
                }},
                {"range": {
                    "comment_count": {
                        "gte": 10
                    }
                }}
            ]
        }
    }}

query = es.search(index='articles_new', body=query_json)
print(query)
