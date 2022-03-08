# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:13 下午
# @Author  : zhengjiawei
# @FileName: __init__.py
# @Software: PyCharm
import abc


class BaseRecall:
    def __init__(self):
        pass

    @abc.abstractmethod
    def recall(self, *args, **kwargs):
        raise NotImplemented
