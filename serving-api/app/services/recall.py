# -*- coding: utf-8 -*-
# @Time    : 2022/1/25 10:52 上午
# @Author  : zhengjiawei
# @FileName: main.py
# @Software: PyCharm
from loader import load_configs
from recall.text_recall.text_recall import TextRecall
from recall.utils import get_query_json, BaseRecall
from recall.vector_recall.vector_recall import VectorRecall


class ReCall:
    def __init__(self,use_vector_recall=True):
        self.use_vector_recall = use_vector_recall
        self.configs = load_configs(path="config.ini", func="recall")
        self.Text_Recall = TextRecall()
        self.Vector_Recall = VectorRecall()
        self.hbase_url = self.configs["hbase_url"]
        self.hbase_port = self.configs["hbase_port"]
        self.redis_url = self.configs["redis_url"]
        self.redis_port = self.configs["redis_port"]
        self.es_url = self.configs["es_url"]
        self.index_name = self.configs["default_index_name"]
        self.vector_dir = self.configs["vector_dir"]
        self.bert_model_path = self.configs["bert_model_path"]
        self.text_recall_nums = self.configs["text_recall_nums"]
        self.summary_recall_nums = self.configs["summary_recall_nums"]
        self.content_recall_nums = self.configs["content_recall_nums"]

    def text_recall(self, query_str):
        query_json = get_query_json(query_str)
        text_recall_id_list = self.Text_Recall.recall(
            query_json, recall_nums=self.text_recall_nums
        )
        print("完成文本召回")
        return text_recall_id_list

    def personalise_recall(self):
        result = "完成个性化召回"
        return result

    def structured_recall(self):
        result = "完成结构化召回"
        return result

    def vector_recall(self, query_str):
        vector_recall_id_list = self.Vector_Recall.recall(
            query_str,
            title_recall_nums=self.text_recall_nums,
            summary_recall_nums=self.summary_recall_nums,
            content_recall_nums=self.content_recall_nums,
        )
        print("完成向量召回")
        return vector_recall_id_list

    def recall(self, query: str):
        query_json = get_query_json(query)
        text_recall_id_list = self.Text_Recall.recall(
            query_json, recall_nums=self.text_recall_nums
        )
        if self.use_vector_recall:
            vector_recall_id_list = self.Vector_Recall.recall(
                query,
                title_recall_nums=self.text_recall_nums,
                summary_recall_nums=self.summary_recall_nums,
                content_recall_nums=self.content_recall_nums,
            )
            text_recall_id_list.extend(vector_recall_id_list)
        ids_list = list(set(text_recall_id_list))
        print('完成召回任务')
        return ids_list


if __name__ == "__main__":
    query_str = "我喜欢学习"
    recall = ReCall()
    # print(recall.text_recall(query_str))
    # print(recall.vector_recall(query_str))
    print(recall.recall(query_str))
