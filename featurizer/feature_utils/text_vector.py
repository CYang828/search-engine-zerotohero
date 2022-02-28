# -*- coding:utf-8 -*-
# @Time   :2022/2/24 5:25 下午
# @Author :Li Meng qi
# @FileName:text_vector.py
from feature_utils import FeatureBase
from transformers import BertModel, BertTokenizer


class TextVector(FeatureBase):
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
        self.model = BertModel.from_pretrained("bert-base-chinese")

    def run(self, data):
        if len(data) > 510:
            data = data[:510]
        print(data)
        print(len(data))
        inputs = self.tokenizer(data, return_tensors="pt")
        print(inputs['input_ids'].shape)
        outputs = self.model(**inputs)
        data_vector = outputs.pooler_output.detach().numpy()[0].reshape(1, -1)
        return data_vector[0].tolist()


# if __name__ == '__main__':
#     textvector = TextVector()
#     res = textvector.run('我喜欢学习！')
#     print(res.shape)