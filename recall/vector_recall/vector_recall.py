# -*- coding: utf-8 -*-
# @Time    : 2022/3/1 3:46 下午
# @Author  : zhengjiawei
# @FileName: vector_recall.py
# @Software: PyCharm
import time

from transformers import BertTokenizer, BertModel

from recall.utils import BaseRecall
from recall.vector_recall.content_vector_recall import ContentVectorRecall
from recall.vector_recall.summary_vector_recall import SummaryVectorRecall
from recall.vector_recall.title_vector_recall import TitleVectorRecall


class VectorRecall(BaseRecall):
    def __init__(self):
        super().__init__()
        self.title_recall = TitleVectorRecall()
        self.summary_recall = SummaryVectorRecall()
        self.content_recall = ContentVectorRecall()
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_model_path)
        self.model = BertModel.from_pretrained(self.bert_model_path)

    def recall(self, query: str, title_recall_nums: int, summary_recall_nums: int, content_recall_nums: int):
        """
        :param query:str
        :param title_recall_nums:int 在title(标题)字段进行向量召回时的召回数量
        :param summary_recall_nums:int 在summary(摘要)字段进行向量召回时的召回数量
        :param content_recall_nums:int 在content(文章内容)字段进行向量召回时的召回数量
        :returns ids:list 召回的文章的id
        """
        inputs = self.tokenizer(query, return_tensors="pt")
        outputs = self.model(**inputs)
        query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
        ids_list = []
        title_recall_id_list = self.title_recall.recall(
            query_array, recall_nums=title_recall_nums)
        summary_recall__id_list = self.summary_recall.recall(
            query_array, recall_nums=summary_recall_nums)
        content_recall__id_list = self.content_recall.recall(
            query_array, recall_nums=content_recall_nums)
        ids_list.extend(title_recall_id_list)
        ids_list.extend(summary_recall__id_list)
        ids_list.extend(content_recall__id_list)
        return ids_list


if __name__ == '__main__':
    query_str = "学习自然语言处理"
    start3 = time.time()
    # query = "期货"
    # tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
    # model = BertModel.from_pretrained('bert-base-chinese')
    # print('参数加载消耗时间：',time.time()-start3)
    # start4 = time.time()
    # inputs = tokenizer(query, return_tensors="pt")
    # outputs = model(**inputs)
    # print('向量转换消耗时间：',time.time()-start4)
    # query_array = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
    vec = VectorRecall()
    ids = vec.recall(query_str, title_recall_nums=10,
                     summary_recall_nums=5, content_recall_nums=3)
    print(ids)
