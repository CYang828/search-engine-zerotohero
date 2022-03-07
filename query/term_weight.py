# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 10:49 上午
# @Author  : zhengjiawei
# @FileName: term_weight.py
# @Software: PyCharm

import json
from collections import defaultdict
from math import log

import happybase
import redis
from sklearn.utils.extmath import softmax


def load_stop_words(stop_word_path):
    """加载停用词
    :param stop_word_path:停用词路径
    :return: 停用词表 list
    """
    # 打开文件
    file = open(stop_word_path, 'r', encoding='utf-8')
    # 读取所有行
    stop_words = file.readlines()
    # 去除每一个停用词前后 空格 换行符
    stop_words = [stop_word.strip() for stop_word in stop_words]
    return stop_words


class TermAnalyze:
    def __init__(self, hbase_url="10.30.89.124", hbase_port=9090,
                 redis_url="10.30.89.124", redis_port=6379):
        self.hbase_url = hbase_url
        self.hbase_port = hbase_port
        self.redis_url = redis_url
        self.redis_port = redis_port
        self.connection = happybase.Connection(host=self.hbase_url, port=self.hbase_port,
                                               timeout=100000)
        self.res = redis.StrictRedis(host=self.hbase_url, port=self.redis_port, db=0)

    def get_vocab_and_top5(self):
        top5_words_dic = defaultdict(int)
        vocab_dic = defaultdict(int)
        table = self.connection.table('document_features')
        for i, each in enumerate(table.scan()):
            # 获得token
            tokens = json.loads(each[1][b'document:tokens'])['tok_fine']
            for token in tokens:
                vocab_dic[token] += 1
            # 获得top5
            top5word = json.loads(each[1][b'document:top5words'])['top5word']
            for word in top5word:
                top5_words_dic[word] += 1

            if i % 50 == 0:
                print(i)
        vocab_dic = json.dumps(vocab_dic)
        self.res.set("idf", vocab_dic)
        top5words = json.dumps(top5_words_dic)
        self.res.set("top5words", top5words)

    def get_content(self):
        # 这里启动接口服务就建立链接，节约每次查询需要的时间
        table = self.connection.table('document_features')
        content = []
        for i, each in enumerate(table.scan(batch_size=1000)):
            # 获得token
            tokens = set(json.loads(each[1][b'document:tokens'])['tok_fine'])
            content.append(tokens)
            if i % 500 == 0:
                print(i)
        return content

    def get_idf(self):
        vocab = set()
        vocab_dic = json.loads(self.res.get("vocab_dic"))
        for each in vocab_dic.keys():
            vocab.add(each)
        content = self.get_content()
        idf = defaultdict(int)
        for i, tokens in enumerate(content):
            for each in vocab:
                if each in tokens:
                    idf[each] += 1
            if i % 100 == 0:
                print(i)
        for key in idf.keys():
            idf[key] = log(len(content) / idf[key])
        return idf

    def get_term_weight(self, query):
        idf = json.loads(self.res.get("idf"))
        weight = []
        for term in query:
            weight.append(idf[term])

        weight = softmax([weight])
        return list(weight[0])


if __name__ == '__main__':
    # query "我喜欢学习"
    query_list = ["我", "喜欢", "学习"]
    query_weight = TermAnalyze().get_term_weight(query_list)
    print(query_weight)
