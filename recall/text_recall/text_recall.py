# -*- coding: utf-8 -*-
# @Time    : 2022/2/25 4:47 下午
# @Author  : zhengjiawei
# @FileName: text_recall.py
# @Software: PyCharm

import json
from elasticsearch import Elasticsearch

from recall.utils import parse_es_content, get_query_json, BaseRecall


class TextRecall(BaseRecall):
    def __init__(self,):
        super().__init__()

    def connect_es(self):
        es = Elasticsearch(
            hosts=self.es_url,
            # 在做任何操作之前，先进行嗅探
            # sniff_on_start=True,
            # # 节点没有响应时，进行刷新，重新连接
            sniff_on_connection_fail=True,
            # # 每 60 秒刷新一次
            sniffer_timeout=60
        )
        return es

    def recall(self, query_json: json, recall_nums: int):
        es = self.connect_es()
        query = es.search(index=self.index_name,
                          body=query_json, size=recall_nums)
        ids_list = parse_es_content(query)
        return ids_list


if __name__ == '__main__':
    query = "学习自然语言处理"
    query_json = get_query_json(query)
    text_recall = TextRecall()
    ids = text_recall.recall(query_json, recall_nums=60)
    print(ids)
