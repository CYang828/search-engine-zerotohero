# -*- coding: utf-8 -*-
# @Time    : 2022/4/1 11:12 上午
# @Author  : zhengjiawei
# @FileName: dataloader.py
# @Software: PyCharm

import horovod.torch as hvd
import pandas as pd
import torch
from collections import defaultdict
from ranker.src.args import get_args
from torch.utils.data import Dataset, DataLoader


# (1)将数据从df中读取，然后传入dataset,dataloader
# 每次从dataloader 中读取批量的数据
# 在dataset中输出label和sparse_features以及dense_features
# gender  age  city  job  education都是离散变量
# 'userid', 'document_id', 'search_token', 'click', 'like', 'comment'
# (2) 从hive中读取数据，然后传入dataset,dataloader
# # 每次从dataloader 中读取批量的数据
#  在search_data中根据将一个样本作为正样本，在文章id中进行采样作为负样本，并且根据样本中的userid在user_data中拿到用户信息
# 一个样本 'userid', 'document_id', 'search_token'，'gender','age', 'city','job', 'education',
# 'click', 'like', 'comment' 标签


class ReadData:

    def __init__(self, train=True, debug=False):
        if train:
            self.search_data = pd.read_csv('dataset/data/train_search_data.csv').head(500000)
        else:
            if debug:
                self.search_data = pd.read_csv('dataset/data/test_search_data.csv').head(100)
            else:
                self.search_data = pd.read_csv('dataset/data/test_search_data.csv')
        self.user_data = pd.read_csv('dataset/data/user_data.csv')
        self.vocab_dic = defaultdict(int)
        with open('dataset/data/vocab.txt', 'r', encoding='utf-8') as f:
            for i, line in enumerate(f.readlines()):
                line = line.strip('\n')
                self.vocab_dic[line] = i
        self.vocab_dic['unk'] = len(self.vocab_dic)


class SearchDataset(Dataset):
    r"""Dataset wrapping tensors.

    Each sample will be retrieved by indexing tensors along the first dimension.

    Arguments:
        *tensors (Tensor): tensors that have the same size of the first dimension.
    """

    def __init__(self, precess_data: ReadData):
        self.precess_data = precess_data
        self.vocab_dic = self.precess_data.vocab_dic
        self.columns_index_dictionary = list(set(list(self.precess_data.search_data.columns) + \
                                                 list(self.precess_data.user_data.columns)))

    def __getitem__(self, index):

        userid = self.precess_data.search_data['userid'][index]
        row = self.precess_data.user_data[self.precess_data.user_data.userid == userid]
        search_token = self.precess_data.search_data['search_token'][index]
        if search_token in self.vocab_dic:
            search_token2id = self.vocab_dic[search_token]
        else:
            search_token2id = self.vocab_dic['unk']
        # document_id = self.precess_data.search_data['document_id'][index]
        sparse_features = {
            # 'document_id': self.precess_data.search_data['document_id'][index],
            'age': int(row['age']),
            'gender': int(row['gender']),
            'city': int(row['city']),
            'job': int(row['job']),
            'education': int(row['education']),
            'search_token': int(search_token2id)
        }
        # dense_feature = {
        #     'search_token': self.precess_data.search_data['search_token'][index]
        # }
        try:
            dense_feature = {'pv': self.precess_data.search_data['pv'][index],
                             'uv': self.precess_data.search_data['uv'][index]}
        except:
            print('pv:',self.precess_data.search_data)
        if 'click' in self.columns_index_dictionary:
            labels = {
                'click': self.precess_data.search_data['click'][index],
                'like': self.precess_data.search_data['like'][index],
                'comment': self.precess_data.search_data['comment'][index],
            }
        else:
            labels = {
                'click': 0,
                'like': 0,
                'comment': 0
            }
        data = (userid,
                sparse_features,
                dense_feature,
                labels)

        return data

    def __len__(self):
        return self.precess_data.search_data.shape[0]


def load_data(args):
    process_train_data = ReadData()
    process_valid_data = ReadData(train=False)
    train_dataset = SearchDataset(process_train_data)
    valid_dataset = SearchDataset(process_valid_data)
    train_sampler = torch.utils.data.distributed.DistributedSampler(
        train_dataset, num_replicas=hvd.size(), rank=hvd.rank())
    valid_sampler = torch.utils.data.distributed.DistributedSampler(
        valid_dataset, num_replicas=hvd.size(), rank=hvd.rank())
    train_dataloader = DataLoader(dataset=train_dataset, batch_size=args.bs,
                                  num_workers=4, pin_memory=False,
                                  sampler=train_sampler)
    valid_dataloader = DataLoader(dataset=valid_dataset, batch_size=args.bs,
                                  num_workers=4, pin_memory=False,
                                  sampler=valid_sampler)
    return train_dataloader, valid_dataloader


if __name__ == '__main__':
    import time

    hvd.init()
    args = get_args()
    start1 = time.time()
    sparse_features = defaultdict()
    train_dataloader, valid_dataloader = load_data(args)
    for data in valid_dataloader:
        print('user_id', data[0])
        print('sparse_features:', data[1])
        print('dense_features:', data[2])
        print('labels:', data[3])
        break
    print('times:', time.time() - start1)
