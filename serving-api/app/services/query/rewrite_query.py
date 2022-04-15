# -*- coding:utf-8 -*-
# @Time   :2022/1/27 4:16 下午
# @Author :Li Meng qi
# @FileName:rewrite_query.py

import pycorrector
import torch
from transformers import BertTokenizer, BertForMaskedLM
from collections import defaultdict
import json
from annoy import AnnoyIndex
from app.services.query.utils.mlemodel import MLEmodel
from app.services.query.utils.tokens import hanlp_token
from nltk.util import pad_sequence, ngrams
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RewriteQuery:
    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )  # 指定设备

        self.tokenizer = BertTokenizer.from_pretrained(
            BASE_DIR + "/query/public_store/macbert4csc-base-chinese"
        )  # 调用tokenizer返回一个句子的input_ids（字典id）、 token_type_ids（第一个句子）、 attention_mask（mask遮罩减小误差）信息

        self.model = BertForMaskedLM.from_pretrained(
            BASE_DIR + "/query/public_store/macbert4csc-base-chinese"
        )  # 初始化模型并加载参数
        self.model = self.model.to(self.device)  # 模型加载到指定设备
        # 读取相似词表
        with open(
            BASE_DIR + "/query/public_store/HIT-IRLab.txt", "r", encoding="GB18030"
        ) as f:  # 注意词表的编码格式是GB18030
            lines = f.readlines()
        # 只用其中相似的词
        self.one2other = defaultdict(list)
        for line in lines:
            line_list = line.strip().split()
            if line_list[0].endswith("="):
                word_list = line_list[1:]
                for i, word in enumerate(word_list):
                    self.one2other[word] = word_list  # 全部考虑
                    # self.one2other[word] = word_list[0:i] + word_list[i + 1:]  # 不考虑自己
        with open(BASE_DIR + "/query/public_store/vocab_dic.bin", "rb") as f_dict:
            w_freq = f_dict.read()
        self.w_freq = json.loads(w_freq)
        temp = defaultdict(int)
        for k, v in self.w_freq.items():
            temp[k] = v
        self.w_freq = temp
        # 加载之前保存的索引文件，目的加快查询速度
        with open(
            BASE_DIR
            + "/query/public_store/tencent-AILab-ChineseEmbedding/tc_word_index.json",
            "r",
        ) as fp:
            self.word_index = json.load(fp)
        self.tc_index = AnnoyIndex(200)
        self.tc_index.load(
            BASE_DIR
            + "/query/public_store/tencent-AILab-ChineseEmbedding/tc_index_build10.index"
        )
        # 反向id==>word映射词表
        self.reverse_word_index = dict(
            [(value, key) for (key, value) in self.word_index.items()]
        )
        # 加载语言模型
        self.language_model = MLEmodel().load()
        print("语言模型加载完毕.")

    def caculate_perplexity(self, tokens, n=2):
        # 计算句子的困惑度
        # 1、获取句子的ngram表示。
        padded_sent = list(
            pad_sequence(
                tokens,
                pad_left=True,
                left_pad_symbol="<s>",
                pad_right=True,
                right_pad_symbol="</s>",
                n=n,
            )
        )
        print(padded_sent)
        print(list(ngrams(padded_sent, n=n)))
        # 2、计算困惑度并返回结果
        return self.language_model.perplexity(list(ngrams(padded_sent, n=n)))

    def corrector_query(self, query):  # 拼写和规则纠正
        corrected_sent, detail = pycorrector.correct(query)
        return corrected_sent, detail

    def grammer_corrector(self, query):  # 语法纠错
        with torch.no_grad():
            outputs = self.model(
                **self.tokenizer(query, padding=True, return_tensors="pt").to(
                    self.device
                )
            )
        _text = self.tokenizer.decode(
            torch.argmax(outputs.logits[0], dim=-1), skip_special_tokens=True
        ).replace(" ", "")
        return _text

    def query_unify(self, tokens):
        candidate = []
        for token in tokens:
            other_words = self.one2other[token]
            if len(other_words) == 0:
                candidate.append(token)
            else:
                other_word2weight = []
                for other_word in other_words:
                    other_word2weight.append((other_word, self.w_freq[other_word]))
                max_other_word = sorted(
                    other_word2weight, key=lambda x: x[1], reverse=True
                )[0][0]
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
                for i, item in enumerate(
                    self.tc_index.get_nns_by_item(self.word_index[word], topk)
                ):
                    results[i].append(
                        self.reverse_word_index[item]
                    )  # self.reverse_word_index[item]用每个索引查询word
            except Exception as e:
                for i in range(topk):
                    results[i] += word
        # 使用语言模型对生成的句子打分并且按照分数由小到大排列（这里是困惑度，越小越好）
        results = [
            ("".join(tokens), self.caculate_perplexity(tokens)) for tokens in results
        ]
        results = sorted(results, key=lambda x: x[1])
        return results


if __name__ == "__main__":
    rq = RewriteQuery()
    query = "我爱你"
    query = hanlp_token(query)
    print("分词后：", query)
    result = rq.query_unify(query)
    print(result)
