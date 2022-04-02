# -*- coding: utf-8 -*-
# @Time    : 2022/3/21 2:23 下午
# @Author  : zhengjiawei
# @FileName: article_information.py
# @Software: PyCharm
import json
import os
import random
from collections import defaultdict, Counter

import happybase
import numpy as np
import pandas as pd
from tqdm import tqdm

from dataset.sampler.utils import generate_userid, load_stop_words, BaseSampler, sample_token


def random_seed(seed):
    np.random.seed(seed)
    random.seed(seed)


random_seed(2022)


class ArticleSampler(BaseSampler):

    def __init__(self):
        super().__init__()
        self.connection = happybase.Connection(host=self.hbase_url, port=self.hbase_port,
                                               timeout=100000)

    def sample(self, debug=False):
        # 在df中选择采样，选择需要的索引
        # 是否点击 1(0.95)
        # 是否点赞 0.05
        # 是否评论 0.01
        if os.path.exists(self.sampler_configs['data_path']+'document_information.csv'):
            document_information = pd.read_csv(self.sampler_configs['data_path']+'document_information.csv')
        else:
            ArticleSampler().get_article()
            document_information = pd.read_csv(self.sampler_configs['data_path']+'document_information.csv')
        if debug:
            self.user_search_max_nums = 50
            self.user_nums = 1000
            document_information = document_information.head(200)

        # 对于每个用户 先选择采样的数量(对多少文章进行点击搜索)
        # 根据文章数量决定每个用户可能交互的文章数量最多为【200，拍脑袋想的】，
        # 然后[0,200]随机选择一个数作为 用户交互的文章数
        #
        # item_information = pd.DataFrame()
        temp_item_list = []
        user_id_list = generate_userid(nums=self.user_nums)

        user_no_click_list = random.sample(user_id_list, int(len(user_id_list) * 0.05))

        user_click_list = [each for each in user_id_list if each not in set(user_no_click_list)]

        length = document_information.shape[0]
        for user_id in tqdm(user_click_list, total=len(user_click_list)):
            sample_nums = random.choice(range(1, self.user_search_max_nums))
            index = np.random.randint(0, length, sample_nums)
            uer_click_data = document_information.iloc[index, :]

            uer_click_data.loc[:, 'userid'] = user_id
            uer_click_data.loc[:, 'click'] = 1  # np.random.binomial(1, 0.95, sample_nums)
            uer_click_data.loc[:, 'like'] = np.random.binomial(1, 0.05, sample_nums)
            uer_click_data.loc[:, 'comment'] = np.random.binomial(1, 0.01, sample_nums)
            temp_item_list.append(uer_click_data)

        for user_id in tqdm(user_no_click_list, total=len(user_no_click_list)):
            sample_nums = random.choice(range(1, self.user_search_max_nums))
            index = np.random.randint(0, length, sample_nums)
            uer_no_search_data = document_information.iloc[index, :]

            uer_no_search_data.loc[:, 'userid'] = user_id
            uer_no_search_data.loc[:, 'click'] = 0
            uer_no_search_data.loc[:, 'like'] = 0
            uer_no_search_data.loc[:, 'comment'] = 0
            temp_item_list.append(uer_no_search_data)

        item_information = pd.concat((each.T for each in tqdm(temp_item_list, total=len(temp_item_list), desc='合并df')),
                                     axis=1).T

        item_information = item_information.reset_index().drop('index', axis=1)
        item_information.loc[:, 'search_token'] = None
        # start = time.time()
        # for i in trange(item_information.shape[0], desc='生成search_token'):
        #     item_information.loc[i, 'search_token'] = str(sample_token(eval(item_information.loc[i, 'clean_token'])))
        item_information['search_token'] = item_information['clean_token'].apply(lambda x: str(sample_token(eval(x))))
        # times = time.time()-start
        # print('循环消耗时间',times)
        #
        # # 调整数据顺序
        item_information_new = item_information.loc[:,
                               ['userid', 'document_id', 'search_token', 'click', 'like', 'comment']]

        item_information_new.to_csv(self.sampler_configs['data_path']+'search_information.csv', index=False)
        # return item_information_new

    def get_article(self, debug=False):
        table = self.connection.table('document_features_02')
        token_list = []
        id_to_token = defaultdict(list)
        for i, each in enumerate(table.scan(batch_size=10)):
            id = json.loads(each[1][b'document:id'].decode())
            token = json.loads(each[1][b'document:tokens'].decode())['tok_fine']
            id_to_token[id] = token
            token_list.extend(token)
            if debug and i != 0 and i % 100 == 0:
                break

        stop_words_list = load_stop_words('../stopwords.txt')
        token_dic = Counter(token_list)
        token_dic = {key: value for key, value in token_dic.items() if key not in stop_words_list}
        # 除去停用词之外，取所有词的数量的5%作为高频词
        # 排序
        token_temp = sorted(token_dic.items(), key=lambda item: item[1], reverse=True)
        high_frequency_words_list = []
        length = int(len(token_dic) * 0.05)
        for each in token_temp[:length]:
            high_frequency_words_list.append(each[0])
        document_token_dic = defaultdict(list)
        for key, values in tqdm(id_to_token.items(), total=len(id_to_token)):
            values_list = []
            for value in values:
                if value not in stop_words_list and value not in high_frequency_words_list:
                    values_list.append(value)

            document_token_dic[key] = values_list

        document_information = pd.DataFrame([document_token_dic]).T
        document_information = document_information.reset_index()
        document_information.columns = ['document_id', 'clean_token']
        document_information.to_csv(self.sampler_configs['data_path']+'document_information.csv', index=False)


if __name__ == '__main__':
    # ArticleSampler().get_article()
    ArticleSampler().sample()
