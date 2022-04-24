# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:23 下午
# @Author  : zhengjiawei
# @FileName: title_vector_recall.py
# @Software: PyCharm
import json
import os
import pickle
import time

import faiss as faiss
import numpy as np
from transformers import BertTokenizer, BertModel

from recall.vector_recall.utils import BaseVectorRecall


class TitleVectorRecall(BaseVectorRecall):
    def __init__(self):
        super().__init__()
        self.title_vector = None
        self.doc_title_id2id = {}
        if os.path.exists(self.vector_dir + "title_vector_array.pkl"):
            self.doc_title_id2id = json.loads(self.res.get("doc_title_id2id"))
            with open(self.vector_dir + "title_vector_array.pkl", "rb") as f:
                self.title_vector = pickle.load(f)
        else:
            self.save_vector()
        self.index = faiss.IndexFlatL2(self.title_vector.shape[1])
        self.index.add(self.title_vector)

    def save_vector(self):
        table = self.connection.table("document_features_02")
        title_vector = []
        doc_id_list = []
        for i, each in enumerate(table.scan(batch_size=10)):
            title_vector_json = json.loads(each[1][b"document:title_vector"].decode())[
                "title_vector"
            ]
            if len(title_vector_json) == 768:
                title_vector.append(title_vector_json)
                doc_id_list.append(json.loads(each[1][b"document:id"].decode()))

        self.title_vector = np.array(title_vector, dtype=np.float32)
        if not os.path.exists(self.vector_dir):
            os.makedirs(self.vector_dir)
        with open(self.vector_dir + "title_vector_array.pkl", "wb") as f:
            pickle.dump(self.title_vector, f)

        self.doc_title_id2id = {i: each for i, each in enumerate(doc_id_list)}
        self.res.set("doc_title_id2id", json.dumps(self.doc_title_id2id))

    def recall(self, query_array, recall_nums: int):
        """
        :param query_array:  需要查询的语句对应的向量
        :param recall_nums: 向量召回的数量
        :return:list(I[0]):list 根据title向量召回文章的id
        """
        D, I = self.index.search(query_array, recall_nums)
        recall_list = list(I[0])
        # print('查询向量时间：', time.time() - start2)
        title_recall_id = []
        for each in recall_list:
            each = str(each)
            if each not in self.doc_title_id2id:
                continue
            else:
                title_recall_id.append(self.doc_title_id2id[each])
        return title_recall_id


if __name__ == "__main__":
    start3 = time.time()
    query = "期货"
    # query2 = '学习'
    tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
    model = BertModel.from_pretrained("bert-base-chinese")
    print("参数加载消耗时间：", time.time() - start3)
    start4 = time.time()
    inputs = tokenizer(query, return_tensors="pt")
    outputs = model(**inputs)

    print("向量转换消耗时间：", time.time() - start4)
    query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
    vec = TitleVectorRecall()
    title_recall_id_list = vec.recall(query_array, recall_nums=40)
    print("title_recall_id_list:", title_recall_id_list)
