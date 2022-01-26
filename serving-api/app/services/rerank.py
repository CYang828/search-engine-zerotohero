# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 2:52 下午
# @Author  : zhengjiawei
# @FileName: rerank.py
# @Software: PyCharm

from builtins import staticmethod


class ReRank:
    def __init__(self, query_list=None):
        self.query_list = query_list

    @staticmethod
    def se_rank():
        rerank_result = "使用 SE-Rank 进行重排"
        return rerank_result


if __name__ == '__main__':

    print(ReRank().se_rank())
