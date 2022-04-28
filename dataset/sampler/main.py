# -*- coding: utf-8 -*-
# @Time    : 2022/3/25 10:59 上午
# @Author  : zhengjiawei
# @FileName: main.py
# @Software: PyCharm
import os

from dataset.sampler.article_information import ArticleSampler
from dataset.sampler.generate_data import get_train_test_data
from dataset.sampler.user_information import UserSampler
from loader import load_configs


def main():
    configs = load_configs("config.ini", func="sampler")
    if not os.path.exists("dataset/data/user_data.csv"):
        UserSampler().sample()
        print("user_data is over")
    if not os.path.exists("dataset/data/document_information.csv"):
        ArticleSampler().get_article()
        print("document_information is over")
    if not os.path.exists("dataset/data/search_information.csv"):
        ArticleSampler().sample()
        print("search_information is over")
    if not os.path.exists("dataset/data/test_search_data.csv"):
        get_train_test_data(configs)
        print("test_search_data is over")


if __name__ == "__main__":
    main()
