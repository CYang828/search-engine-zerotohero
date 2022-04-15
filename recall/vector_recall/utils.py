# -*- coding: utf-8 -*-
# @Time    : 2022/3/25 4:39 下午
# @Author  : zhengjiawei
# @FileName: utils.py
# @Software: PyCharm
import abc

import happybase
import redis

from recall.utils import BaseRecall


class BaseVectorRecall(BaseRecall):
    def __init__(self):
        super().__init__()
        self.connection = happybase.Connection(
            host=self.hbase_url,
            port=self.hbase_port,
            timeout=100000,
            protocol="compact",
            transport="framed",
        )
        self.res = redis.StrictRedis(host=self.redis_url, port=self.redis_port, db=0)

    @abc.abstractmethod
    def save_vector(self, *args, **kwargs):
        raise NotImplemented

    @abc.abstractmethod
    def recall(self, *args, **kwargs):
        raise NotImplemented
