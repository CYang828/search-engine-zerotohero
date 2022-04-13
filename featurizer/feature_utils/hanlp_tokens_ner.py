# -*- coding:utf-8 -*-
# @Time   :2022/2/24 5:12 下午
# @Author :Li Meng qi
# @FileName:hanlp_tokens_ner.py
from feature_utils import FeatureBase
import hanlp
import json


class HanlpTokensNer(FeatureBase):
    def __init__(self, hanlp_model):
        self.HanLP = hanlp_model

    def run(self, data):
        data = data[:512]
        results_document = self.HanLP(data, tasks='ner')  # 精分
        tok_fine = json.dumps({'tok_fine': results_document['tok/fine']})
        ner_msra = results_document['ner/msra']
        ner = {}
        for entity, entity_class, _, _ in ner_msra:
            if entity_class not in ner.keys():
                ner[entity_class] = [entity]
            else:
                # 一篇文章中可能存在多个相同实体，此语句进行过滤
                if entity not in ner[entity_class]:
                    ner[entity_class].append(entity)
        return tok_fine, json.dumps(ner)
