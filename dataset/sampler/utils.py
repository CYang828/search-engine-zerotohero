# -*- coding: utf-8 -*-
# @Time    : 2022/3/23 11:47 上午
# @Author  : zhengjiawei
# @FileName: utils.py
# @Software: PyCharm
import abc
import json
import random

import numpy as np
from pymongo import MongoClient

from loader import load_configs


def load_stop_words(stop_word_path):
    """加载停用词
    :param stop_word_path:停用词路径
    :return: 停用词表 list
    """
    # 打开文件
    file = open(stop_word_path, 'r', encoding='utf-8')
    # 读取所有行
    stop_words = file.readlines()
    # 去除每一个停用词前后 空格 换行符
    stop_words = [stop_word.strip() for stop_word in stop_words]
    return stop_words


def generate_userid(nums) -> list:
    """"
    :return userid_list，存放用户的userid
    """
    ids = [each for each in range(nums)]
    userid_list = []
    for each in ids:
        id = 'userid_' + (len(str(nums)) - len(str(each))) * str(0) + str(each)
        userid_list.append(id)
    return userid_list


def save_data_to_mongo(mongo_url, mongo_port, mongo_db, table_name, df):
    client = MongoClient(host=mongo_url, port=mongo_port)
    db = client[mongo_db]
    crowd = db[table_name]
    crowd.insert(json.loads(df.T.to_json()).values())


def sample_token(token_list):
    temp_list = list(set(token_list))
    if len(temp_list) >= 10:
        nums = random.sample([2, 3], 1)[0]
        token_lis = random.sample(temp_list, nums)
    else:
        token_lis = []
    return token_lis


def random_seed(seed):
    np.random.seed(seed)
    random.seed(seed)


class BaseSampler:
    base_configs = load_configs(path='../../config.ini', func='base')
    recall_configs = load_configs(path='../../config.ini', func='recall')
    sampler_configs = load_configs(path='../../config.ini', func='sampler')

    def __init__(self):
        self.mongo_url = self.base_configs['mongo_url']
        self.mongo_port = self.base_configs['mongo_port']
        self.mongo_db = self.base_configs['mongo_db']
        self.hbase_url = self.base_configs['hbase_url']
        self.hbase_port = self.base_configs['hbase_port']

        self.user_nums = self.sampler_configs['user_nums']
        self.user_search_max_nums = self.sampler_configs['user_search_max_nums']

    @abc.abstractmethod
    def sample(self, *args, **kwargs):
        raise NotImplemented

    def save_data(self, table_name, df):
        save_data_to_mongo(mongo_url=self.mongo_url, mongo_port=self.mongo_port, mongo_db=self.mongo_db,
                           table_name=table_name, df=df)
