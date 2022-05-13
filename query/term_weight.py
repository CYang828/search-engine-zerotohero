# -*- coding: utf-8 -*-
# @Time    : 2021/12/8 10:49 上午
# @Author  : zhengjiawei
# @FileName: term_weight.py
# @Software: PyCharm

import json
from collections import defaultdict
from math import log

import happybase
import numpy as np
import redis
from tqdm import tqdm


def softmax(x):
    """Compute the softmax of vector x."""
    exp_x = np.exp(x)
    softmax_x = exp_x / np.sum(exp_x)
    return softmax_x


def load_stop_words(stop_word_path):
    """加载停用词
    :param stop_word_path:停用词路径
    :return: 停用词表 list
    """
    # 打开文件
    file = open(stop_word_path, "r", encoding="utf-8")
    # 读取所有行
    stop_words = file.readlines()
    # 去除每一个停用词前后 空格 换行符
    stop_words = [stop_word.strip() for stop_word in stop_words]
    return stop_words


class TermAnalyze:
    def __init__(
            self,
            hbase_url="10.30.89.124",
            hbase_port=9090,
            query_list=None,
            redis_url="10.30.89.124",
            redis_port=6379,
    ):
        self.hbase_url = hbase_url
        self.hbase_port = hbase_port
        self.redis_url = redis_url
        self.redis_port = redis_port
        self.query_list = query_list
        self.connection = happybase.Connection(
            host=self.hbase_url, port=self.hbase_port, timeout=100000
        )
        self.res = redis.StrictRedis(host=self.hbase_url, port=self.redis_port, db=0)

    def get_vocab_and_top5(self):
        print('执行 get_vocab_and_top5 函数')
        top5_words_dic = defaultdict(int)
        vocab_dic = defaultdict(int)
        table = self.connection.table("document_features")
        for i, each in enumerate(table.scan()):
            # 获得token
            tokens = json.loads(each[1][b"document:tokens"])["tok_fine"]
            for token in tokens:
                vocab_dic[token] += 1
            # 获得top5
            top5word = json.loads(each[1][b"document:top5words"])["top5word"]
            for word in top5word:
                top5_words_dic[word] += 1

            if i % 500 == 0:
                print(i)
        vocab_dic = json.dumps(vocab_dic)
        self.res.set("vocab_dic", vocab_dic)
        top5words = json.dumps(top5_words_dic)
        self.res.set("top5words", top5words)

    def get_content(self):
        print('执行get_content 函数')
        # 这里启动接口服务就建立链接，节约每次查询需要的时间
        table = self.connection.table("document_features")
        content = []
        for i, each in enumerate(table.scan(batch_size=1000)):
            # 获得token
            tokens = set(json.loads(each[1][b"document:tokens"])["tok_fine"])
            content.append(tokens)
            if i % 500 == 0:
                print(i)
        print('get_content 函数 结束')
        return content

    def get_idf(self):
        print('执行 get_idf 函数')
        vocab = set()
        vocab_dic = json.loads(self.res.get("vocab_dic"))
        for each in vocab_dic.keys():
            vocab.add(each)
        top_words = set()
        top5words = json.loads(self.res.get("top5words"))

        for each in top5words.keys():
            top_words.add(each)

        content = self.get_content()
        vocab_fre = defaultdict(int)
        top5_fre = defaultdict(int)
        for tokens in tqdm(content, desc='content'):
            for each in vocab:
                if each in tokens:
                    vocab_fre[each] += 1
            for every in top_words:
                if every in tokens:
                    top5_fre[every] += 1

        vocab_idf = defaultdict(int)
        for key in tqdm(vocab_fre.keys(), desc='vocab_fre'):
            vocab_idf[key] = log(len(content) / vocab_fre[key])
        top5_idf = defaultdict(int)
        for key in tqdm(top5_fre.keys(), desc='top5_fre'):
            top5_idf[key] = log(len(content) / top5_fre[key])
        vocab_idf = json.dumps(vocab_idf)
        self.res.set("vocab_idf", vocab_idf)

        top5_idf = json.dumps(top5_idf)
        self.res.set("top5_idf", top5_idf)

    def get_term_weight(self):
        if self.res.exists("vocab_idf"):
            vocab_idf = json.loads(self.res.get("vocab_idf"))
            top5_idf = json.loads(self.res.get("top5_idf"))

        else:
            if self.res.exists("vocab_dic"):
                self.get_idf()
            else:
                self.get_vocab_and_top5()
            vocab_idf = json.loads(self.res.get("vocab_idf"))
            top5_idf = json.loads(self.res.get("top5_idf"))

        weight0 = []
        weight1 = []
        for term in self.query_list:
            if term in vocab_idf:
                weight0.append(vocab_idf[term])
            else:
                weight0.append(0)
            if term in top5_idf:
                weight1.append(top5_idf[term])
            else:
                weight1.append(0)
        weight_new = [weight0[i] + weight1[i] for i in range(len(weight0))]
        weight = softmax([weight_new])
        return list(weight)


if __name__ == "__main__":
    # 保存文档中字(格式  vocab:词频)对应的字典，以及top5word对应的字典(格式 vocab:词频)到redis中
    # TermAnalyze().get_vocab_and_top5()

    # 根据公式(idf = log(预料库的文档总数/包含该词的文档数+1)) 计算idf并保存在redis中
    #
    TermAnalyze().get_idf()
    query_list = ["我", "喜欢", "学习"]
    query_weight = TermAnalyze(query_list=query_list).get_term_weight()
    print(query_weight)
