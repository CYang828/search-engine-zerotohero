# -*- coding: utf-8 -*-
# @Time    : 2022/3/25 10:59 上午
# @Author  : zhengjiawei
# @FileName: main.py
# @Software: PyCharm
from dataset.sampler.article_information import ArticleSampler
from dataset.sampler.generate_data import get_train_test_data
from dataset.sampler.user_information import UserSampler
from loader import load_configs


def main():
    configs = load_configs('../../config.ini', func='sampler')
    UserSampler().sample()
    ArticleSampler().get_article()
    ArticleSampler().sample()
    get_train_test_data(configs)


if __name__ == '__main__':
    main()
