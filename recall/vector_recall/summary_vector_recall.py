# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:30 下午
# @Author  : zhengjiawei
# @FileName: summary_vector_recall.py
# @Software: PyCharm

import json
import os
import pickle

import faiss as faiss
import numpy as np

from recall.vector_recall import BaseVectorRecall


class SummaryVectorRecall(BaseVectorRecall):
    def __init__(self):
        super().__init__()
        self.summary_vector = None
        self.doc_summary_id2id = {}

    def save_vector(self):
        table = self.connection.table('document_features_02')
        summary_vector = []
        doc_id_list = []
        for i, each in enumerate(table.scan(batch_size=10)):
            summary_vector_json = json.loads(each[1][b'document:excerpt_vector'].decode())[
                'excerpt_vector']
            if len(summary_vector_json) == 768:
                summary_vector.append(summary_vector_json)
                doc_id_list.append(json.loads(
                    each[1][b'document:id'].decode()))

        self.summary_vector = np.array(summary_vector, dtype=np.float32)

        if not os.path.exists(self.vector_dir):
            os.makedirs(self.vector_dir)

        with open(self.vector_dir + "summary_vector_array.pkl", 'wb') as f:
            pickle.dump(self.summary_vector, f)
        self.doc_summary_id2id = {
            i: each for i, each in enumerate(doc_id_list)}
        self.res.set('doc_summary_id2id', json.dumps(self.doc_summary_id2id))

    def recall(self, query: str, recall_nums: int):
        """
        :param query: str 需要查询的语句
        :param recall_nums: 向量召回的数量
        :return:list(I[0]):list 根据title向量召回文章的id
        """
        if os.path.exists(self.vector_dir + 'summary_vector_array.pkl'):
            self.doc_summary_id2id = json.loads(
                self.res.get('doc_summary_id2id'))
            with open(self.vector_dir + 'summary_vector_array.pkl', 'rb') as f:
                self.summary_vector = pickle.load(f)
        else:
            self.save_vector()

        index = faiss.IndexFlatL2(self.summary_vector.shape[1])
        index.add(self.summary_vector)

        inputs = self.tokenizer(query, return_tensors="pt")
        outputs = self.model(**inputs)
        query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
        D, I = index.search(query_array, recall_nums)
        recall_list = list(I[0])
        summary_recall_id = []
        for each in recall_list:
            each = str(each)
            if each not in self.doc_summary_id2id:
                continue
            else:
                summary_recall_id.append(self.doc_summary_id2id[each])

        return summary_recall_id


if __name__ == '__main__':
    query = "期货"
    vec = SummaryVectorRecall()
    id_list = vec.recall(query, recall_nums=40)
    print(id_list)
