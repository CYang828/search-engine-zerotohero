# -*- coding: utf-8 -*-
# @Time    : 2022/1/25 10:52 上午
# @Author  : zhengjiawei
# @FileName: main.py
# @Software: PyCharm


class ReCall:
    def __init__(self, query_list=None):
        self.query_list = query_list

    def text_recall(self):
        result = "完成文本召回"
        return result

    def personalise_recall(self):
        result = "完成个性化召回"
        return result

    def structured_recall(self):
        result = "完成结构化召回"
        return result

    def vector_recall(self):
        result = "完成向量召回"
        return result


if __name__ == '__main__':
    query_list = ["我喜欢学习"]
    recall = ReCall(query_list)
    print(recall.structured_recall())
