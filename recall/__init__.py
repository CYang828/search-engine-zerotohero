# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:13 下午
# @Author  : zhengjiawei
# @FileName: __init__.py
# @Software: PyCharm
import abc

from loader import load_configs


class BaseRecall:
    # config_path = os.path.join(os.path.dirname(__file__), "config.ini")
    configs = load_configs(path='../config.ini', func='recall')

    def __init__(self):
        self.hbase_url = self.configs['hbase_url']
        self.hbase_port = self.configs['hbase_port']
        self.redis_url = self.configs['redis_url']
        self.redis_port = self.configs['redis_port']
        self.es_url = self.configs['es_url']
        self.index_name = self.configs['default_index_name']
        self.vector_dir = self.configs['vector_dir']
        self.bert_model_path = self.configs['bert_model_path']
        self.text_recall_nums = self.configs['text_recall_nums']
        self.summary_recall_nums = self.configs['summary_recall_nums']
        self.content_recall_nums = self.configs['content_recall_nums']

    @abc.abstractmethod
    def recall(self, *args, **kwargs):
        raise NotImplemented
