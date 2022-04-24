# -*- coding:utf-8 -*-
# @Time   :2022/2/24 5:25 下午
# @Author :Li Meng qi
# @FileName:text_vector.py
from featurizer.feature_utils import FeatureBase
from transformers import BertModel, BertTokenizer
import os
import torch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TextVector(FeatureBase):
    def __init__(self, device_id):
        self.tokenizer = BertTokenizer.from_pretrained(
            BASE_DIR + "/data/best_model_ckpt"
        )
        self.model = BertModel.from_pretrained(BASE_DIR + "/data/best_model_ckpt")
        # config['device'] = 'cuda' if torch.cuda.is_available() else 'cpu'
        if torch.cuda.is_available():
            self.device = "cuda:" + str(device_id)
            self.model.to(self.device)
            print("bert model 加载到了{}.".format(self.device))
        else:
            self.device = "cpu"

    def run(self, data):
        if len(data) > 510:
            data = data[:510]
        inputs = self.tokenizer(data, return_tensors="pt")
        # print(inputs)
        inputs = {key: value.to(self.device) for key, value in inputs.items()}
        outputs = self.model(**inputs)
        data_vector = outputs.pooler_output.detach().to("cpu").numpy()[0].reshape(1, -1)
        return data_vector[0].tolist()


if __name__ == "__main__":
    textvector = TextVector(device_id=1)
    res = textvector.run("我喜欢学习！")
    print(res)
