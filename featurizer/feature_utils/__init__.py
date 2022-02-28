# -*- coding:utf-8 -*-
# @Time   :2022/2/24 4:44 下午
# @Author :Li Meng qi
# @FileName:__init__.py.py
from abc import ABCMeta, abstractmethod


class FeatureBase(metaclass=ABCMeta):

    @abstractmethod
    def run(self, data):
        raise NotImplementedError
