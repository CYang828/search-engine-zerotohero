# -*- coding:utf-8 -*-
# @Time   :2022/1/11 2:39 下午
# @Author :Mengqi Li
# @FileName:tokens.py
import hanlp

HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)  # 先加载模型


def hanlp_token(query):
    """
    调用hanlp分词
    :param query: 一句话
    :return: 分词结果
    """
    if query.strip() == '':  # 这里如果是空下面的分词会报错
        return ['']
    results_document = HanLP(query, tasks='ner')  # 精分
    return results_document['tok/fine']


if __name__ == '__main__':
    print(hanlp_token(' '))
