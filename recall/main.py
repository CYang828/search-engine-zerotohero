# -*- coding: utf-8 -*-
# @Time    : 2022/3/1 3:43 下午
# @Author  : zhengjiawei
# @FileName: main.py
# @Software: PyCharm
import time
from multiprocessing import Manager

from recall.text_recall.text_recall import TextRecall
from recall.utils import get_query_json, BaseRecall
from recall.vector_recall.vector_recall import VectorRecall


class Recall(BaseRecall):
    def __init__(self, use_vector_recall=True):
        super().__init__()
        self.use_vector_recall = use_vector_recall
        self.text_recall = TextRecall()
        if self.use_vector_recall:
            self.vector_recall = VectorRecall()

    def recall(self, query: str):
        query_json = get_query_json(query)
        text_recall_id_list = self.text_recall.recall(
            query_json, recall_nums=self.text_recall_nums)
        if self.use_vector_recall:
            vector_recall_id_list = self.vector_recall.recall(query, title_recall_nums=self.text_recall_nums,
                                                              summary_recall_nums=self.summary_recall_nums,
                                                              content_recall_nums=self.content_recall_nums)
            text_recall_id_list.extend(vector_recall_id_list)
        ids_list = list(set(text_recall_id_list))
        return ids_list


if __name__ == '__main__':
    start1 = time.time()
    query_str = "学习自然语言处理"
    recall = Recall()
    ids = recall.recall(query_str)
    print('召回时间：', time.time() - start1)
    print(ids)
