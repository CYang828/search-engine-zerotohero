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

from recall.utils import BaseRecall


class BaseVectorRecall(BaseRecall):
    def __init__(self):
        super().__init__()
        self.connection = happybase.Connection(host=self.hbase_url, port=self.hbase_port,
                                               timeout=100000)
        self.res = redis.StrictRedis(
            host=self.redis_url, port=self.redis_port, db=0)
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_model_path)
        self.model = BertModel.from_pretrained(self.bert_model_path)

    @abc.abstractmethod
    def save_vector(self, *args, **kwargs):
        raise NotImplemented

    @abc.abstractmethod
    def recall(self, *args, **kwargs):
        raise NotImplemented

