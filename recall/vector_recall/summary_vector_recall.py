# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:30 下午
# @Author  : zhengjiawei
# @FileName: summary_vector_recall.py
# @Software: PyCharm

import json
import pickle

import faiss as faiss
import numpy as np

from recall import VectorRecall


class SummaryVectorRecall(VectorRecall):
    def __init__(self):
        super().__init__()

    def save_vector(self):
        table = self.connection.table('document_features_02')
        summary_vector = []
        doc_id_list = []
        for i, each in enumerate(table.scan(batch_size=10)):
            summary_vector_json = json.loads(each[1][b'document:excerpt_vector'].decode())['excerpt_vector']
            if len(summary_vector_json) == 768:
                summary_vector.append(summary_vector_json)
                doc_id_list.append(json.loads(each[1][b'document:id'].decode()))

        summary_vector = np.array(summary_vector, dtype=np.float32)
        with open("summary_vector_array.pkl", 'wb') as f:
            pickle.dump(summary_vector, f)
        doc_summary_id2id = {i: each for i, each in enumerate(doc_id_list)}
        self.res.set('doc_summary_id2id', json.dumps(doc_summary_id2id))

    def faiss_vector_recall(self, query: str, recall_nums: int = 40):
        """
        :param query: str 需要查询的语句
        :param recall_num: 向量召回的数量
        :return:list(I[0]):list 根据title向量召回文章的id
        """
        with open('summary_vector_array.pkl', 'rb') as f:
            summary_vectors = pickle.load(f)

        doc_summary_id2id = json.loads(self.res.get('doc_summary_id2id'))

        index = faiss.IndexFlatL2(summary_vectors.shape[1])
        index.add(summary_vectors)

        inputs = self.tokenizer(query, return_tensors="pt")
        outputs = self.model(**inputs)
        query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
        D, I = index.search(query_array, recall_nums)
        recall_list = list(I[0])
        summary_recall_id = [doc_summary_id2id[str(each)] for each in recall_list]
        return summary_recall_id


if __name__ == '__main__':
    query = "期货"
    vec = SummaryVectorRecall()
    faiss_summary_vector_recall = vec.faiss_vector_recall(query, recall_nums=40)
    print("faiss_summary_vector_recall:",faiss_summary_vector_recall)