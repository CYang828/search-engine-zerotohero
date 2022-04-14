# -*- coding:utf-8 -*-
# @Time   :2022/1/27 4:16 下午
# @Author :Li Meng qi
# @FileName:rewrite.py
import pycorrector
import torch
from transformers import BertTokenizer, BertForMaskedLM
from collections import defaultdict
import json
from annoy import AnnoyIndex
from query.utils.mle_model import MLEmodel
from query.tokenization import Tokenization
from nltk.util import pad_sequence, ngrams
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RewriteQuery:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # 调用tokenizer返回一个句子的input_ids（字典id）、 token_type_ids（第一个句子）、 attention_mask（mask遮罩减小误差）信息
        self.tokenizer = BertTokenizer.from_pretrained(
            BASE_DIR + "/query/model_data/macbert4csc-base-chinese")
        # 初始化模型并加载参数
        self.model = BertForMaskedLM.from_pretrained(
            BASE_DIR + "/query/model_data/macbert4csc-base-chinese")
        # 模型加载到指定设备
        self.model = self.model.to(self.device)
        # 加载相似词表
        self.load_similar_words()
        # 加载词与词频
        self.load_word_freq()
        # 加载之前保存的索引文件，目的加快查询速度
        self.load_index_word_vector()
        # 加载语言模型
        self.language_model = MLEmodel().load()

    def load_similar_words(self):
        # 读取相似词表（注意词表的编码格式是GB18030）
        with open(BASE_DIR + "/query/model_data/HIT-IRLab.txt", 'r', encoding='GB18030') as f:
            lines = f.readlines()
        # 只用其中相似的词
        self.one2other = defaultdict(list)
        for line in lines:
            line_list = line.strip().split()
            if line_list[0].endswith('='):
                word_list = line_list[1:]
                for i, word in enumerate(word_list):
                    self.one2other[word] = word_list  # 全部考虑
                    # self.one2other[word] = word_list[0:i] + word_list[i + 1:]  # 不考虑自己

    def load_word_freq(self):
        with open(BASE_DIR + "/query/model_data/vocab_dic.bin", 'rb') as f_dict:
            w_freq = f_dict.read()
        self.w_freq = json.loads(w_freq)
        temp = defaultdict(int)
        for k, v in self.w_freq.items():
            temp[k] = v
        self.w_freq = temp

    def load_index_word_vector(self):
        with open(BASE_DIR + "/query/model_data/tencent-AILab-ChineseEmbedding/tc_word_index.json", 'r') as fp:
            self.word_index = json.load(fp)
        self.tc_index = AnnoyIndex(200)
        self.tc_index.load(BASE_DIR + "/query/model_data/tencent-AILab-ChineseEmbedding/tc_index_build10.index")
        # 反向id==>word映射词表
        self.reverse_word_index = dict([(value, key) for (key, value) in self.word_index.items()])

    def caculate_perplexity(self, tokens, n=2):
        # 计算句子的困惑度
        # 1、获取句子的ngram表示。
        padded_sent = list(pad_sequence(tokens, pad_left=True, left_pad_symbol="<s>",
                                        pad_right=True, right_pad_symbol="</s>", n=n))
        print(padded_sent)
        print(list(ngrams(padded_sent, n=n)))
        # 2、计算困惑度并返回结果
        return self.language_model.perplexity(list(ngrams(padded_sent, n=n)))

    def query_corrector(self, query):
        """
        语法纠错
        """
        with torch.no_grad():
            outputs = self.model(**self.tokenizer(query, padding=True, return_tensors='pt').to(self.device))
        _text = self.tokenizer.decode(torch.argmax(outputs.logits[0], dim=-1), skip_special_tokens=True).replace(' ',
                                                                                                                 '')
        return _text

    def query_unify(self, tokens):
        """
        query归一
        """
        candidate = []
        for token in tokens:
            other_words = self.one2other[token]
            if len(other_words) == 0:
                candidate.append(token)
            else:
                other_word2weight = []
                for other_word in other_words:
                    other_word2weight.append((other_word, self.w_freq[other_word]))
                max_other_word = sorted(other_word2weight, key=lambda x: x[1], reverse=True)[0][0]
                candidate.append(max_other_word)
        return candidate

    def query_extend(self, query, topk=10):  # 还需要优化，加入语言模型或者beam-search方法来提高生成句子的准确性
        """
        对query进行扩展
        :param query:分词后的query，类型列表
        :return: 返回扩展后的结果
        """
        # model.logscore("never", "language is".split())  # 打分
        results = [[] for _ in range(topk)]
        for word in query:
            try:  # OOV问题还用原来的词
                # get_nns_by_item基于annoy查询词最近的10个向量，返回结果是个list，里面元素是索引
                for i, item in enumerate(self.tc_index.get_nns_by_item(self.word_index[word], topk)):
                    # self.reverse_word_index[item]用每个索引查询word
                    results[i].append(self.reverse_word_index[item])
            except Exception as e:
                for i in range(topk):
                    results[i] += word
        # 使用语言模型对生成的句子打分并且按照分数由小到大排列（这里是困惑度，越小越好）
        results = [(''.join(tokens), self.caculate_perplexity(tokens)) for tokens in results]
        results = sorted(results, key=lambda x: x[1])
        return results


if __name__ == '__main__':
    rq = RewriteQuery()
    tokenizer = Tokenization()
    query = '支持向量积教雪视频😊'
    print('原来query：', query)
    query = rq.query_corrector(query)
    print('纠错后：', query)
    query_token, _ = tokenizer.hanlp_token_ner(query)
    print('分词后：', query_token)
    result = rq.query_unify(query_token)
    print('归一后：', result)
    result = rq.query_extend(query_token)
    print('拓展后：', result)