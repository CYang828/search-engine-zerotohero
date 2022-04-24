# -*- coding:utf-8 -*-
# @Time   :2022/3/8 4:15 下午
# @Author :Li Meng qi
# @FileName:intent_recognition.py
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from query.tokenization import Tokenization
import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class IntentRecognition:
    def __init__(self, n_pick_topics=20, n_pick_docs=20):
        # 设定主题数量
        self.n_pick_topics = n_pick_topics
        # 返回相关主题中文章的数量
        self.n_pick_docs = n_pick_docs
        self._load_corpus()

    def _load_corpus(self):
        f = open(
            BASE_DIR
            + "/query/model_data/intent-recognition/cleaned_document_remove_stopwords_token.pkl",
            "rb",
        )
        self.corpus_data = pickle.load(f)
        f.close()

    def fit(self):
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(self.corpus_data)
        lsa = TruncatedSVD(self.n_pick_topics)
        X2 = lsa.fit_transform(X)
        self._save("vectorizer", vectorizer)
        self._save("lsa", lsa)
        self._save("X2", X2)

    def _save(self, model_name, obj):
        with open(
            BASE_DIR + "/query/model_data/intent-recognition/" + model_name + ".pkl",
            "wb",
        ) as f:
            pickle.dump(obj, f)

    def _load(self, model_name):
        with open(
            BASE_DIR + "/query/model_data/intent-recognition/" + model_name + ".pkl",
            "rb",
        ) as f:
            model = pickle.load(f)
        return model

    def predict(self, query):
        tokenize = Tokenization()
        query_tokens, _ = tokenize.hanlp_token_ner(query)
        query = [" ".join(query_tokens)]
        vectorizer = self._load("vectorizer")
        lsa = self._load("lsa")
        X2 = self._load("X2")
        topic_docs_id = [
            X2[:, t].argsort()[: -(self.n_pick_docs + 1) : -1]
            for t in range(self.n_pick_topics)
        ]
        quert_tfidf = vectorizer.transform(query)
        # 使用lsa对其降维
        lsa_query = lsa.transform(quert_tfidf)
        # 获取权重最大的主题
        topic_index = lsa_query[0].argsort()[:-2:-1]
        # print(topic_index)
        results = []
        # 取出该主题中的前n_pick_docs的document
        for i in range(self.n_pick_docs):
            # print("    doc %d" % i)
            # print("\t" + self.corpus_data[topic_docs_id[int(topic_index)][i]][:200])
            results.append(self.corpus_data[topic_docs_id[int(topic_index)][i]])
        return results


if __name__ == "__main__":
    intentrecognition = IntentRecognition()
    # intentrecognition.fit()
    re = intentrecognition.predict("想去美国留学")
    print(len(re))
