# -*- coding:utf-8 -*-
# @Time   :2022/1/27 4:19 下午
# @Author :Li Meng qi
# @FileName:mle_model.py
from nltk.util import pad_sequence
from nltk.util import ngrams
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm import MLE
import dill as pickle
import time
import pickle

class MLEmodel:
    def __init__(self, model_path='/Users/lmq/Desktop/query/Build_NgramZ_Language_Model/kilgariff_ngram_model.pkl'):
        self.model_path = model_path

    def read(self, sentence_tokens_path='sentences_tokens.pickle'):
        f = open(sentence_tokens_path, 'rb')
        self.tokenized_text = pickle.load(f)  # 所有的分词
        f.close()
        print(f'读取完毕，一共{len(self.tokenized_text)}个句子。')

    def fit(self, n=3):
        self.read()
        train_data, padded_sents = padded_everygram_pipeline(n, self.tokenized_text)
        self.model = MLE(n)
        print('字典的大小：', len(self.model.vocab))
        print('training...')
        start_time = time.time()
        self.model.fit(train_data, padded_sents)
        end_time = time.time()
        seconds = end_time - start_time
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        print('trained, use time %02d:%02d:%02d' % (h, m, s))
        # print(model.vocab)
        print('saving...')
        self.save()
        print('saved')

    def save(self):
        with open(self.model_path, 'wb') as fout:
            pickle.dump(self.model, fout)

    def load(self):
        with open(self.model_path, 'rb') as fin:
            model_loaded = pickle.load(fin)
        return model_loaded

    def caculate_perplexity(self, tokens, n=2):
        # 计算句子的困惑度
        # 1、获取句子的ngram表示。
        padded_sent = list(pad_sequence(tokens, pad_left=True, left_pad_symbol="<s>",
                                        pad_right=True, right_pad_symbol="</s>", n=n))
        print(padded_sent)
        print(list(ngrams(padded_sent, n=n)))
        # 2、计算困惑度并返回结果
        return self.language_model.perplexity(list(ngrams(padded_sent, n=n)))


if __name__ == '__main__':
    mle = MLEmodel()
    # mle.fit()
    model = mle.load()
    print(model.logscore("never", "language is".split()))
    print(model.perplexity())
