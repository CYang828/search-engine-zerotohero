# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:34 下午
# @Author  : zhengjiawei
# @FileName: content_vector_recall.py
# @Software: PyCharm

import json
import pickle

import faiss as faiss
import numpy as np

from recall import VectorRecall


class ContentVectorRecall(VectorRecall):
    def __init__(self):
        super().__init__()

    def save_vector(self):
        table = self.connection.table('document_features_02')
        content_vector = []
        doc_id_list = []
        print('start getting clean_content_vector')
        for i, each in enumerate(table.scan(batch_size=10)):
            content_vector_json = json.loads(each[1][b'document:clean_content_vector'].decode())['clean_content_vector']
            if len(content_vector_json) == 768:
                content_vector.append(content_vector_json)
                doc_id_list.append(json.loads(each[1][b'document:id'].decode()))

        content_vector = np.array(content_vector, dtype=np.float32)
        with open("content_vector_array.pkl", 'wb') as f:
            pickle.dump(content_vector, f)
        doc_content_id2id = {i: each for i, each in enumerate(doc_id_list)}
        self.res.set('doc_content_id2id', json.dumps(doc_content_id2id))

    def faiss_vector_recall(self, query: str, recall_nums: int = 40):
        """
        :param query: str 需要查询的语句
        :param recall_num: 向量召回的数量
        :return:list(I[0]):list 根据title向量召回文章的id
        """
        with open('content_vector_array.pkl', 'rb') as f:
            content_vectors = pickle.load(f)

        doc_content_id2id = json.loads(self.res.get('doc_content_id2id'))

        index = faiss.IndexFlatL2(content_vectors.shape[1])
        index.add(content_vectors)

        inputs = self.tokenizer(query, return_tensors="pt")
        outputs = self.model(**inputs)
        query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
        D, I = index.search(query_array, recall_nums)
        recall_list = list(I[0])
        summary_recall_id = [doc_content_id2id[str(each)] for each in recall_list]
        return summary_recall_id


if __name__ == '__main__':
    query = "期货"
    vec = ContentVectorRecall()
    # vec.get_save_content_vector()
    content_recall_id_list = vec.faiss_vector_recall(query, recall_nums=40)
    print("content_recall_id_list:", content_recall_id_list)
