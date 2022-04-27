# -*- coding:utf-8 -*-
# @Time   :2022/4/26 4:10 下午
# @Author :Li Meng qi
# @FileName:build_tencent_vector_index.py

import json
from collections import OrderedDict
from gensim.models import KeyedVectors
from annoy import AnnoyIndex

tc_wv_model = KeyedVectors.load_word2vec_format('model_data/tencent-AILab-ChineseEmbedding/Tencent_AILab_ChineseEmbedding.txt',
                                                binary=False)
# 把txt文件里的词和对应的向量，放入有序字典
word_index = OrderedDict()
for counter, key in enumerate(tc_wv_model.vocab.keys()):
    word_index[key] = counter

# 本地保存
with open('model_data/tencent-AILab-ChineseEmbedding/tc_word_index.json', 'w') as fp:
    json.dump(word_index, fp)

# 腾讯词向量是两百维的
tc_index = AnnoyIndex(200)
i = 0
for key in tc_wv_model.vocab.keys():
    v = tc_wv_model[key]
    tc_index.add_item(i, v)
    i += 1

tc_index.build(10)

# 将这份index存到硬盘
tc_index.save('model_data/Tencent_AILab_ChineseEmbedding/tc_index_build10.index')

# 反向id==>word映射词表
reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

# get_nns_by_item基于annoy查询词最近的10个向量，返回结果是个list，里面元素是索引
for item in tc_index.get_nns_by_item(word_index[u'卖空'], 10):
    print(reverse_word_index[item])  # 用每个索引查询word