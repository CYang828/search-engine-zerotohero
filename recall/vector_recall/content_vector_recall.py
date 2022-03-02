# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:34 下午
# @Author  : zhengjiawei
# @FileName: content_vector_recall.py
# @Software: PyCharm

import json
import os
import pickle

import faiss as faiss
import numpy as np

from recall.vector_recall import BaseVectorRecall


class ContentVectorRecall(BaseVectorRecall):
    def __init__(self):
        super().__init__()
        self.content_vector = None
        self.doc_content_id2id = {}

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

            if i % 1000 == 0:
                print(f"正在获得第{i}个文章向量")

        self.content_vector = np.array(content_vector, dtype=np.float32)

        if not os.path.exists(self.vector_dir):
            os.makedirs(self.vector_dir)

        with open(self.vector_dir + "content_vector_array.pkl", 'wb') as f:
            pickle.dump(self.content_vector, f)
        self.doc_content_id2id = {i: each for i, each in enumerate(doc_id_list)}
        self.res.set('doc_content_id2id', json.dumps(self.doc_content_id2id))

    def faiss_vector_recall(self, query: str, recall_nums: int = 40):
        """
        :param query: str 需要查询的语句
        :param recall_nums: 向量召回的数量
        :return:list(I[0]):list 根据content向量召回文章的id
        """
        if os.path.exists(self.vector_dir + 'content_vector_array.pkl'):
            self.doc_content_id2id = json.loads(self.res.get('doc_content_id2id'))
            print("path:", self.vector_dir + 'content_vector_array.pkl')
            with open(self.vector_dir + 'content_vector_array.pkl', 'rb') as f:
                self.content_vector = pickle.load(f)
        else:
            self.save_vector()

        index = faiss.IndexFlatL2(self.content_vector.shape[1])
        index.add(self.content_vector)

        inputs = self.tokenizer(query, return_tensors="pt")
        outputs = self.model(**inputs)
        query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
        D, I = index.search(query_array, recall_nums)
        recall_list = list(I[0])
        content_recall_id = [self.doc_content_id2id[str(each)] for each in recall_list]
        return content_recall_id


if __name__ == '__main__':
    query = "期货"
    vec = ContentVectorRecall()
    content_id_list = vec.faiss_vector_recall(query, recall_nums=40)
    print("content_recall_id_list:", content_id_list)
