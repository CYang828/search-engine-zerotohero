# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 2:05 下午
# @Author  : zhengjiawei
# @FileName: rank.py
# @Software: PyCharm
from builtins import staticmethod

from ranker.src.test import main


class Rank:
    def __init__(self, query_list=None):
        self.query_list = query_list

    @staticmethod
    def tf_ranking():
        result_rank = "使用TF-Rank框架进行精排"
        return result_rank

    @staticmethod
    def mmoe():
        print("使用多目标排序算法mmoe")
        result_rank = main()
        return result_rank

    @staticmethod
    def ltr():
        result_rank = "使用Unbias的LTR"
        return result_rank

    @staticmethod
    def re_transformer():
        result_rank = "使用 Transformer 改进经典精排模型"
        return result_rank


if __name__ == "__main__":
    print(Rank().mmoe())
