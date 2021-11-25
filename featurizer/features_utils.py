##!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Time   :${2021/11/25} ${14:13}
# @Author :Mengqi Li
# @FileName:${NAME}.py
import hanlp
import re
import json

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
def hanlp_token_and_ner(contents):
    """
    :param contents: 是一个列表，列表中每个元素是一个句子
    :return: tok_fine json字符串，样例{'tok_fine':['', '']} ; ner json字符串{'LOCATION':{'地球', '澳大利亚'}, 'DATE':{'世纪'}……}
    """
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


# 过滤HTML中的标签
def extract_article(htmlstr):
    if isinstance(htmlstr, float):
        print(htmlstr)
        return ''
    re_h = re.compile('<.*?>')  # HTML标签
    s = re_h.sub('', htmlstr)
    s = s.replace(' ', '')
    return s
if __name__ == '__main__':
    contents = ['2021年HanLPv2.1为生产环境带来次世代最先进的多语种NLP技术。', '李明来到北京立方庭参观自然语义科技公司。']
    tok_fine, ner_msra = hanlp_token_and_ner(contents)
    print(tok_fine)
    print(ner_msra)

