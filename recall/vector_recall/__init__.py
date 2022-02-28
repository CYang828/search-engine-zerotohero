# -*- coding: utf-8 -*-
# @Time    : 2022/2/25 4:36 下午
# @Author  : zhengjiawei
# @FileName: __init__.py.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:13 下午
# @Author  : zhengjiawei
# @FileName: __init__.py
# @Software: PyCharm
import abc

import happybase
import redis
from transformers import BertModel, BertTokenizer


class VectorRecall:
    def __init__(self, hbase_url="10.30.89.124", hbase_port=9090,
                 redis_url="10.30.89.124", redis_port=6379):
        """
        hbase_url:hbase url
        hbase_port:hbase 端口
        redis_url:redis url
        redis_port:redis 端口
        """
        self.hbase_url = hbase_url
        self.hbase_port = hbase_port
        self.redis_url = redis_url
        self.redis_port = redis_port
        self.connection = happybase.Connection(host=self.hbase_url, port=self.hbase_port,
                                               timeout=100000)
        self.res = redis.StrictRedis(host=self.redis_url, port=self.redis_port, db=0)
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
        self.model = BertModel.from_pretrained("bert-base-chinese")

    @abc.abstractmethod
    def save_vector(self, *args, **kwargs):
        raise NotImplemented

    @abc.abstractmethod
    def faiss_vector_recall(self, *args, **kwargs):
        raise NotImplemented
