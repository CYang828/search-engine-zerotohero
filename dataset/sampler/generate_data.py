# -*- coding: utf-8 -*-
# @Time    : 2022/3/21 2:16 下午
# @Author  : zhengjiawei
# @FileName: generate_data.py
# @Software: PyCharm
import pandas as pd

from loader import load_configs


def get_train_test_data(config):
    search_information = pd.read_csv('search_information.csv')
    test_search_data = search_information.sample(n=config['test_data_nums'], random_state=2022, axis=0)
    train_search_data = search_information[~search_information.index.isin(test_search_data.index)]

    test_search_data.to_csv('test_search_data.csv', index=False)
    train_search_data.to_csv('train_search_data.csv', index=False)


if __name__ == '__main__':
    configs = load_configs('../../config.ini',func='sampler')
    get_train_test_data(configs)
