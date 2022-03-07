# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:23 下午
# @Author  : zhengjiawei
# @FileName: title_vector_recall.py
# @Software: PyCharm
import json
import pickle

import faiss as faiss
import numpy as np

from recall import VectorRecall


class TitleVectorRecall(VectorRecall):
    def __init__(self):
        super().__init__()

    def save_vector(self):
        """
        1、保存title向量到pickle文件中
        2、保存文章的id和title_vector位置索引的对应关系
        """
        table = self.connection.table('document_features_02')
        title_vector = []
        doc_id_list = []
        for i, each in enumerate(table.scan(batch_size=10)):
            title_vector_json = json.loads(each[1][b'document:title_vector'].decode())['title_vector']
            if len(title_vector_json) == 768:
                title_vector.append(title_vector_json)
                doc_id_list.append(json.loads(each[1][b'document:id'].decode()))

        title_vector = np.array(title_vector, dtype=np.float32)
        with open("title_vector_array.pkl", 'wb') as f:
            pickle.dump(title_vector, f)
        doc_title_id2id = {i: each for i, each in enumerate(doc_id_list)}
        self.res.set('doc_title_id2id', json.dumps(doc_title_id2id))

    def faiss_vector_recall(self, query: str, recall_nums: int = 40):
        """
        query: str 需要查询的语句
        recall_num: 向量召回的数量
        return:list(I[0]):list 根据title向量召回文章的id
        """
        with open('title_vector_array.pkl', 'rb') as f:
            title_vector = pickle.load(f)

        doc_title_id2id = json.loads(self.res.get('doc_title_id2id'))
        index = faiss.IndexFlatL2(title_vector.shape[1])
        index.add(title_vector)

        inputs = self.tokenizer(query, return_tensors="pt")
        outputs = self.model(**inputs)
        query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
        D, I = index.search(query_array, recall_nums)
        recall_list = list(I[0])
        title_recall_id = [doc_title_id2id[str(each)] for each in recall_list]
        return title_recall_id


if __name__ == '__main__':
    query = "期货"
    vec = TitleVectorRecall()
    title_recall_id_list = vec.faiss_vector_recall(query, recall_nums=40)
    print("title_recall_id_list:", title_recall_id_list)
