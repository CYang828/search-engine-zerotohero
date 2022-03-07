# -*- coding:utf-8 -*-
# @Time   :2022/2/28 5:07 下午
# @Author :Li Meng qi
# @FileName:__init__.py.py

from abc import ABCMeta, abstractmethod


class BaseExtract(metaclass=ABCMeta):

    @abstractmethod
    def extract(self, row_data):
        raise NotImplementedError