# -*- coding: utf-8 -*-
# @Time    : 2022/2/28 9:04 下午
# @Author  : zhengjiawei
# @FileName: utils.py
# @Software: PyCharm
import abc

from loader import load_configs


def get_query_json(query, boost_title=3, boost_summary=2, boost_content=1):
    query_json = {"query": {"match": {"content": query}}}
    # query_json = {
    #     "query": {
    #         "bool": {
    #             "must": [
    #                 {
    #                     "match": {
    #                         "title": {
    #                             "query": query,
    #                             "boost": boost_title
    #                         }
    #                     }
    #                 },
    #                 {
    #                     "match": {
    #                         "content": {
    #                             "query": query,
    #                             "boost": boost_content
    #                         }
    #                     }
    #                 }
    #                 , {
    #                     "match": {
    #                         "excerpt": {
    #                             "query": query,
    #                             "boost": boost_summary
    #                         }
    #                     }
    #
    #                 }
    #             ]
    #         }
    #     }
    # }
    return query_json


def parse_es_content(query_dict):
    ids_list = []
    query_list = query_dict["hits"]["hits"]
    length = len(query_list)
    for i in range(length):
        id = query_list[i]["_source"]["id"]
        ids_list.append(id)
    return ids_list


class BaseRecall:
    configs = load_configs(path="config.ini", func="recall")

    def __init__(self):
        self.hbase_url = self.configs["hbase_url"]
        self.hbase_port = self.configs["hbase_port"]
        self.redis_url = self.configs["redis_url"]
        self.redis_port = self.configs["redis_port"]
        self.es_url = self.configs["es_url"]
        self.index_name = self.configs["default_index_name"]
        self.vector_dir = self.configs["vector_dir"]
        self.bert_model_path = self.configs["bert_model_path"]
        self.text_recall_nums = self.configs["text_recall_nums"]
        self.summary_recall_nums = self.configs["summary_recall_nums"]
        self.content_recall_nums = self.configs["content_recall_nums"]

    @abc.abstractmethod
    def recall(self, *args, **kwargs):
        raise NotImplemented
