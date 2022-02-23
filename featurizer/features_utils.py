##!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Time   :${2021/11/25} ${14:13}
# @Author :Mengqi Li
# @FileName:${NAME}.py
import hanlp
import re
import json
import gensim
import numpy as np
import time
import datetime
import os
from gensim.models import word2vec
from bert_serving.client import BertClient
from bs4 import BeautifulSoup as bs

bc = BertClient() # 声明bert客户端，这里是为了下面bert编码句子成向量作准备
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEPARATOR = r'@'
RE_SENTENCE = re.compile(r'(\S.+?[.!?])(?=\s+|$)|(\S.+?)(?=[\n]|$)', re.UNICODE)
AB_SENIOR = re.compile(r'([A-Z][a-z]{1,2}\.)\s(\w)', re.UNICODE)
AB_ACRONYM = re.compile(r'(\.[a-zA-Z]\.)\s(\w)', re.UNICODE)
UNDO_AB_SENIOR = re.compile(r'([A-Z][a-z]{1,2}\.)' + SEPARATOR + r'(\w)', re.UNICODE)
UNDO_AB_ACRONYM = re.compile(r'(\.[a-zA-Z]\.)' + SEPARATOR + r'(\w)', re.UNICODE)

HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)  # 先加载模型


def replace_with_separator(text, separator, regexs):
    replacement = r"\1" + separator + r"\2"
    result = text
    for regex in regexs:
        result = regex.sub(replacement, result)
    return result


# 以下代码选用的是hanlp中提供的基于规则的分句子方法（还有一种基于模型分句）
def split_sentence(text, best=True):
    text = re.sub('([。！？\?])([^”’])', r"\1\n\2", text)
    text = re.sub('(\.{6})([^”’])', r"\1\n\2", text)
    text = re.sub('(\…{2})([^”’])', r"\1\n\2", text)
    text = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', text)
    for chunk in text.split("\n"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if not best:
            yield chunk
            continue
        processed = replace_with_separator(chunk, SEPARATOR, [AB_SENIOR, AB_ACRONYM])
        for sentence in RE_SENTENCE.finditer(processed):
            sentence = replace_with_separator(sentence.group(), r" ", [UNDO_AB_SENIOR, UNDO_AB_ACRONYM])
            yield sentence


# 特征提取函数
def hanlp_token_and_ner(contents, use_split_sentence=False):
    """
    :param contents: 是一篇文章
    :param use_split_sentence: 为True是对文章先分句，再逐句进行分词、ner
    :return: tok_fine json字符串，样例{'tok_fine':['', '']} ; ner json字符串{'LOCATION':['地球', '澳大利亚'], 'DATE':['世纪']……}
    """
    if not use_split_sentence:
        results_document = HanLP(contents, tasks='ner')  # 精分
        tok_fine = json.dumps({'tok_fine': results_document['tok/fine']})
        ner_msra = results_document['ner/msra']
        ner = {}
        for entity, entity_class, _, _ in ner_msra:
            if entity_class not in ner.keys():
                ner[entity_class] = [entity]
            else:
                if entity not in ner[entity_class]:  # 一篇文章中可能存在多个相同实体，此语句进行过滤
                    ner[entity_class].append(entity)
        return tok_fine, json.dumps(ner)
    else:
        sentence_list = [sentence for sentence in split_sentence(contents)]
        results_document = HanLP(sentence_list, tasks='ner')  # 精分
        content_fine = []
        for sentence_fine in results_document['tok/fine']:
            content_fine += sentence_fine
        tok_fine = json.dumps({'tok_fine': content_fine})
        ner_msra = results_document['ner/msra']
        ner = {}
        for sentence_ner in ner_msra:
            for entity, entity_class, _, _ in sentence_ner:
                if entity_class not in ner.keys():
                    ner[entity_class] = [entity]
                else:
                    if entity not in ner[entity_class]:  # 一篇文章中可能存在多个相同实体，此语句进行过滤
                        ner[entity_class].append(entity)
        return tok_fine, json.dumps(ner)


# 过滤HTML中的标签
def extract_article(htmlstr):
    if isinstance(htmlstr, float):
        print(htmlstr)
        return ''
    # 第一个版本从html中提取文本
    # re_h = re.compile('<.*?>')  # HTML标签
    # s = re_h.sub('', htmlstr)
    # s = s.replace(' ', '')
    # return s
    # 第二个版本从html中提取文本
    result = bs(htmlstr).get_text()
    return result


# 对文本进行向量化，（借用bert对文本进行了编码）该实现方法是调用服务生成句子向量bert-as-service
# 第一次运行需要安装包并且启动服务才
# 1、安装包
# pip install bert-serving-server  # server
# pip install bert-serving-client  # client, independent of `bert-serving-server`
# pip install tensorflow==1.14.0  # 需要一个较低的tensorflow版本，不然会报错
# 2、开启服务（bert中文模型下载地址：https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip）
# bert-serving-start -model_dir chinese_L-12_H-768_A-12 -num_worker=1 -max_seq_len 512
# 3、使用示例
# from bert_serving.client import BertClient
# bc = BertClient()
# bc.encode(["今天天气真好","我感冒了"])
def document_vector(document):
    """
    使用bert对文本进行编码
    :param document: 文本
    :return: 文本的向量表示，这里是768维，是列表list类型
    """
    document_vector = bc.encode([document])[0].tolist()
    return document_vector


# 对文本进行向量化，（使用腾讯训练的词向量进行向量化）
wv_from_text = gensim.models.KeyedVectors.load(
    BASE_DIR + '/featurizer' + '/tencent_word_embedding/Tencent_AILab_ChineseEmbedding.bin', mmap='r')
found = 0


def compute_ngrams(word, min_n, max_n):
    extended_word = word
    ngrams = []
    for ngram_length in range(min_n, min(len(extended_word), max_n) + 1):
        for i in range(0, len(extended_word) - ngram_length + 1):
            ngrams.append(extended_word[i:i + ngram_length])
    return list(set(ngrams))


# 返回词向量，词在词表中不存在的用其ngram相加后的向量代替
def word_vector(word, min_n=1, max_n=3):
    # 确认词向量维度
    # word_size = wv_from_text.wv.syn0[0].shape[0]
    word_size = wv_from_text.vector_size
    # 如果在词典之中，直接返回词向量
    if word in wv_from_text.index_to_key:
        global found
        found += 1
        return wv_from_text[word]
    else:
        ngrams = compute_ngrams(word, min_n=min_n, max_n=max_n)
        # 不在词典的情况下，计算与词相近的词向量
        word_vec = np.zeros(word_size, dtype=np.float32)
        ngrams_found = 0
        ngrams_single = [ng for ng in ngrams if len(ng) == 1]
        ngrams_more = [ng for ng in ngrams if len(ng) > 1]
        # 先只接受2个单词长度以上的词向量
        for ngram in ngrams_more:
            if ngram in wv_from_text.index_to_key:
                word_vec += wv_from_text[ngram]
                ngrams_found += 1
                # print(ngram)
        # 如果，没有匹配到，那么最后是考虑单个词向量
        if ngrams_found == 0:
            for ngram in ngrams_single:
                if ngram in wv_from_text.index_to_key:
                    word_vec += wv_from_text[ngram]
                    ngrams_found += 1
        if word_vec.any():  # 只要有一个不为0
            return word_vec / max(1, ngrams_found)
        else:
            print('all ngrams for word %s absent from model' % word)
            return 0


if __name__ == '__main__':
    # contents = ['2021年HanLPv2.1为生产环境带来次世代最先进的多语种NLP技术。', '李明来到北京立方庭参观自然语义科技公司。']
    # contents = '广而告之零、前言在机器学习建模过程中，正则化是控制模型复杂度，对抗过拟合，追求更优预测效果的重要手段。本文从多个角度对L2正则化进行讲解，内容涵盖线性回归、岭回归、贝叶斯、主成分分析、奇异值分解、模型自由度、偏置-方差平衡等。本文提纲为：介绍线性回归（LinearRegression）和岭回归（RidgeRegression），从岭回归引入L2正则化（L2Regularization）；在贝叶斯视角下，从最大化似然概率（LikelihoodProbability）和后验概率（PosteriorProbability）的角度理解最小二乘和L2正则化；从主成分分析（principlecomponentanalysis）的角度理解L2正则化，阐述L2正则化如何对方差小的主成分方向进行惩罚；从偏置（bias）-方差（variance）平衡和模型自由度的角度理解L2正则化如何对抗过拟合。本文先导知识包括：线性代数（矩阵乘法、向量内积、转置、线性独立、向量正交、线性空间及其基、逆矩阵、矩阵的秩和迹、矩阵特征值和特征向量），概率（期望、方差、协方差、多元正态分布、贝叶斯公式）。一、线性回归、岭回归与L2正则化为维向量，为标量。令与之间满足：是服从正态分布的随机误差，且对于每一个是独立同分布的。如果把增加一维成为，其中，再令向量为，则[1.1]可以写成向量形式：下文默认向量包含且共有维。训练集由个向量和标量构成：。线性回归的任务就是从训练集中学习最优的参数。何谓最优？一种方法是定义损失函数如下：对每一个样本计算模型预测的平方误差（squarederror），在个样本上取平均就得到均方误差mse（meansquarederror）。mse衡量了个预测值与对应真实值之间的总差异。把每一个训练样本的转置作为一行构造一个矩阵。模型对个样本的预测是维向量：将个真实输出也列成维向量。mse损失函数可以写成：能够使达到最小的就是线性回归问题的最小二乘解（leastsquare）。是一个二次函数，具有唯一的最小值。满足必要条件：解此方程得到：于是模型对训练集的预测就是：称为变换矩阵。它的迹（trace，对角线元素之和）是：其中为单位矩阵。上式利用了的迹等于的迹这个事实。可以看到的迹就是模型参数的数量。将变换矩阵的迹定义为模型的自由度，则最小二乘线性回归模型的自由度就是模型参数的数量。最小化就是寻找使达到最小。由的列线性组合而成的向量集合是一个线性空间——的列空间。最小化就是在的列空间中寻找一个与距离最小的向量，即在列空间上的投影。就是这个投影。式[1.7]存在一个问题。假如的列线性相关，即训练样本的各特征线性相关，则的秩小于。那么矩阵不满秩，为奇异矩阵不可逆。于是[1.7]不再成立。为了避免这个问题，可人为将的对角线元素增大一个量，变成。其中为单位矩阵。在矩阵的对角线上加上一个值增高了它的“山岭”。山岭增高后的矩阵变成可逆的。把它代入[1.7]得到：这就是岭回归（RidgeRegression）的解公式。岭回归的预测值是：按照上面对自由度的定义，岭回归的自由度应该是变换矩阵的迹。它比最小二乘的自由度是大是小呢？这里先卖个关子，留待后文揭晓。最小二乘解是使均方误差mse最小的解。那么岭回归的解是否最小化了什么东西呢？请看下面的损失函数：满足极小值必要条件：解该式得到：可看到最优化。是mse加上的倍。就是L2正则化项。它其实是的模（长度）的平方。它度量的是各个系数的绝对值大小。将它作为惩罚项加入损失函数，迫使最优解的各系数接近0。是一个超参数，它控制着的重要程度。若则没有正则化；若则各参数只能是0。相对于样本个数越大则正则化越强。下节将从贝叶斯观点出发，为理解L2正则提供另一视角。二、贝叶斯观点下的最小二乘和L2正则所谓训练，是指观察到一组训练样本和目标值（即），找到使后验概率达到最大的。根据贝叶斯公式：等号右侧分子的第一项是似然概率，第二项是先验概率。第一节提到线性回归问题预设：其中服从。且每一个的独立。那么向量就服从多元正态分布。似然概率的密度函数是：对施加，并将一些与无关的常数项整理到一起，得到：注意右边的第二项。撇开与无关的系数它就是负的均方误差mse。也就是说最小化mse等价于最大化似然概率。但是我们的终极目标是最大化后验概率。最小二乘解最大化的是似然概率，相当于预设的先验概率与取值无关。如果预设服从多元正态分布，则后验概率可以写为：对施加并将无关的常数项整理到一起，得到：忽略与无关的常数项和系数项，最大化后验概率等价于最小化带L2正则项的mse损失函数。正则系数反比于的先验方差。越大相当于先验方差越小，的取值越集中。这就是控制了模型的自由度。第一节说过将模型自由度定义为变换矩阵的迹。那么变换矩阵的迹与此处的自由度有关么？下一节将从主成分角度出发为理解L2正则提供又一个洞见。同时L2正则化对模型自由度的影响也将清晰起来。三、主成分与L2正则本节假设训练集中的样本经过中心化，也就是每一个分量的平均值都为0。那么训练样本的协方差矩阵就是：是对称矩阵，它的特征值都是非负实数（可以多重）。这些特征值对应的特征向量线性独立且两两正交（此事实本文不证明，可参考[1]）。令为对角矩阵，其对角线上的元素为从大到小排列的特征值。令为以这些特征值对应的标准特征向量做列组成的矩阵。这些标准特征向量两两正交且模都为1。于是有。由特征值和特征向量的定义，有：也就是：一个对称矩阵（这里是）可分解成一个正交矩阵和一个对角矩阵的乘积形式[3.3]。这称为对称矩阵的谱分解。的个列向量构成维空间的一组标准正交基，也就是一个标准正交坐标系。令：的第一列为个样本在坐标系第一个坐标轴上的投影，第二列是在第二个坐标轴上的投影，依此类推。的个行向量构成一组新的维特征向量。它们的协方差矩阵为：其非对角线元素为0，即个特征两两不相关。的第一个分量的方差最大，为的第一大特征值。的第二个分量的方差次大，为的第二大特征值，依此类推。的列分别为的第一主成分、第二主成分，依此类推。若只有个非零特征值，则只有个方差不为0的特征。由于只是原数据在新坐标系的投影，这说明原数据的真实维度只有维。也可以把排在后面的小特征值忽略，因为在这些小特征值对应的特征方向上原数据方差很小，可以认为是噪声。主成分分析是一种降维手段，将原始数据降到真实维度或更低的维度。降维后的数据保留了原始数据的绝大部分信息。新数据各维之间摆脱了共线性，有利于减少模型的方差。要谈主成分与L2正则的关系，就需要先介绍奇异值分解。若有个非0特征值，则它们的平方根就是矩阵的奇异值。用这个奇异值做对角线元素组成一个的对角矩阵。用对应的标准特征向量做列组成一个的矩阵。再用这个维向量做列组成一个的矩阵。则有：因为的列为对称矩阵的标准特征向量，它们模为1且两两正交。于是。如此：这就是矩阵的奇异值分解。另外，的列可以张成的列空间，因为对于任意一个列空间中的向量：上式第四个等号成立是因为只有前个特征值非0，对于0特征值对应的特征向量有：所以有。另外的列两两正交：最后，的列向量是标准的（模为1）：有个非0特征值，说明的秩为。它的列空间为维空间。则的列构成列空间的一组标准正交基。且的个列是经过标准化的的前个主成分。看一下线性回归最小二乘解的公式（推导过程中记住,以及）：以的列作为列空间的基，上式最后一个等号告诉我们是在列空间上的投影（与之前的结论一致）。是的主成分的线性组合，系数为在各个主成分方向上的投影长度。L2正则化终于要登场了：在带L2正则化的岭回归问题中，仍是的列的线性组合，但组合系数是在的各个主成分方向上的投影长度再各自乘上一个系数。该系数大于0而小于1。越大则系数越接近0，越小则越接近1。同时大特征值对应的系数比小特征值对应的系数更接近1。若为0则所有系数都为1，退化成为。于是可以看到，相比于最小二乘，岭回归在预测的时候对每个主成分方向都施加了一个惩罚（乘上小于1的系数）。正则系数越大则惩罚越强。为0则无惩罚。相对于方差较大的主成分方向惩罚较轻；相对于方差较小的主成分方向，惩罚较重。如果认为方差较小的方向来自噪声，则L2正则压缩了噪声的影响，降低了的方差。主成分分析原样保留大方差方向，去掉小方差方向，相当于一个硬选择。而L2正则根据方差的大小施加不同程度的惩罚，相当于软选择。接下来再看自由度。式[3.13]表明岭回归的变换矩阵为：它的迹为：可见，加入L2正则化之后模型的自由度小于参数个数。四、偏置-方差权衡与L2正则化的作用对于一个新样本点，其真实输出为，模型预测值为。将平方误差取期望得到期望误差。这里取期望的随机因素包括真实值的随机性以及训练集的随机性（这导致了的随机性）：第一步根据平方的期望等于期望的平方加上方差。第二步利用事实：训练集外再观察一次得到的和预测值之间的是独立的。该式表明模型的期望误差等于数据本身的方差，模型预测值的方差，模型预测偏置的平方三部分加和。偏置与方差是一对矛盾。模型复杂度高则偏差小方差大，产生过拟合。模型复杂度低则偏差大方差小，产生欠拟合。模型调参就是通过超参数控制模型复杂度，在偏置与方差权衡中找到一个平衡点使得期望误差最小。上节说过L2正则压抑小方差主成分方向的影响从而降低预测的方差。这是有代价的。它使模型的预测变得有偏。考察一下最小二乘解和岭回归解在训练样本集上预测值和（式[1.8]和式[1.11]）的均值和方差：由此看出，最小二乘解的预测是无偏的。的协方差矩阵为：预测值第个分量的方差为，是变换矩阵的第个对角线元素。全体个预测值的方差之和为：而岭回归的预测值的期望为：估计不再无偏。但是的协方差矩阵是：预测值第个分量的方差为，是矩阵的第个对角线元素。全体个预测值的方差之和为：可见L2正则化牺牲了偏置，但减小了预测值的方差。模型自由度即模型复杂性。根据线性模型自由度的定义，岭回归的自由度低于最小二乘的自由度。L2正则化降低模型复杂度，使方差更低而偏差更高。在上图中就是向着左侧靠拢。通过调节正则化系数可以控制模型自由度，在bias-variancetrade-off中寻找最佳平衡点，追求最优的泛化效果。五、参考数目线性代数及其应用(豆瓣)统计学习基础(第2版)(英文)(豆瓣)'
    # tok_fine, ner_msra = hanlp_token_and_ner(contents)
    # print(json.loads(tok_fine))
    # print(json.loads(ner_msra))
    # print('-' * 50)
    # tok_fine, ner_msra = hanlp_token_and_ner(contents, True)
    # print(json.loads(tok_fine))
    # print(json.loads(ner_msra))

    print(document_vector(' '))
