# -*- coding: utf-8 -*-
# @Time    : 2022/3/1 3:43 下午
# @Author  : zhengjiawei
# @FileName: main.py
# @Software: PyCharm
import time
from collections import defaultdict

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
            query_json, recall_nums=self.text_recall_nums
        )
        if self.use_vector_recall:
            vector_recall_id_list = self.vector_recall.recall(
                query,
                title_recall_nums=self.text_recall_nums,
                summary_recall_nums=self.summary_recall_nums,
                content_recall_nums=self.content_recall_nums,
            )
            text_recall_id_list.extend(vector_recall_id_list)
        ids_list = list(set(text_recall_id_list))
        return ids_list

    def multi_recall(self, query_list: list):
        ids_dict = defaultdict(list)
        text_recall_id_dict = self.text_recall.multi_recall(
            query_list
        )
        print('text_recall_id_dict:', text_recall_id_dict)
        if self.use_vector_recall:
            vector_recall_id_dict = self.vector_recall.multi_recall(
                query_list,
                title_recall_nums=self.text_recall_nums,
                summary_recall_nums=self.summary_recall_nums,
                content_recall_nums=self.content_recall_nums,
            )
            print('vector_recall_id_dict:', vector_recall_id_dict)
            for each in query_list:
                ids_dict[each] = list(set(text_recall_id_dict[each] + vector_recall_id_dict[each]))

            return ids_dict
        else:
            return text_recall_id_dict


if __name__ == "__main__":
    query = ["学习自然语言处理", "股票期货"]
    recall = Recall()
    ids = recall.multi_recall(query)
