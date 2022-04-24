# -*- coding: utf-8 -*-
# @Time    : 2022/3/24 9:18 下午
# @Author  : zhengjiawei
# @FileName: evaluation.py
# @Software: PyCharm
import time
from functools import partial
from multiprocessing import Manager, Pool
from multiprocessing.dummy import Process

import pandas as pd
from tqdm import trange, tqdm

from recall.main import Recall

data_test = pd.read_csv("dataset/data/test_search_data.csv")


def eva(recall, document_id_list, search_token_list, return_dict, num):
    length = len(document_id_list)
    total = 0
    for i in trange(length):
        ids = recall.recall(search_token_list[i])
        if document_id_list[i] in ids:
            total += 1
    return_dict[num] = total


def eva_one(recall, temp_zip):
    document_id = temp_zip[0]
    search_token = temp_zip[1]
    ids = recall.recall(search_token)
    if document_id in ids:
        num = 1
    else:
        num = 0
    return num


def text_vector_recall():
    nums = data_test.shape[0]
    document_id_list = []
    search_token_list = []
    for i in range(nums):
        search_token_temp = eval(data_test.loc[i, "search_token"])
        if len(search_token_temp) > 0:
            search_token_str = "".join(each for each in search_token_temp)
            search_token_list.append(search_token_str)
            document_id_list.append(data_test.loc[i, "document_id"])

    assert len(document_id_list) == len(search_token_list)
    recall = Recall(use_vector_recall=False)
    start = time.time()
    document_id_list = document_id_list[:10]
    search_token_list = search_token_list[:10]
    p = Pool(processes=10)

    total = list(
        tqdm(
            p.imap(
                partial(eva_one, recall=recall),
                list(zip(document_id_list, search_token_list)),
            )
        )
    )
    p.close()
    p.join()
    print(total)
    print("times:", time.time() - start)


def fast_eva_recall():
    nums = data_test.shape[0]
    document_id_list = []
    search_token_list = []
    for i in range(nums):
        search_token_temp = eval(data_test.loc[i, "search_token"])
        if len(search_token_temp) > 0:
            search_token_str = "".join(each for each in search_token_temp)
            search_token_list.append(search_token_str)
            document_id_list.append(data_test.loc[i, "document_id"])

    assert len(document_id_list) == len(search_token_list)
    manager = Manager()
    return_dict = manager.dict()
    recall = Recall()
    start = time.time()
    jobs = []
    for i in range(5):
        if i != 4:
            temp_document_id = document_id_list[i * 10000 : (i + 1) * 10000]
            temp_search_token = search_token_list[i * 10000 : (i + 1) * 10000]
        else:
            temp_document_id = document_id_list[i * 10000 :]
            temp_search_token = search_token_list[i * 10000 :]
        p = Process(
            target=eva,
            args=(recall, temp_document_id, temp_search_token, return_dict, i),
        )
        jobs.append(p)
        p.start()
    for proc in jobs:
        proc.join()
    print("*" * 80)
    hit_rate = sum([each for each in return_dict.values()]) / len(document_id_list)
    print("times:", time.time() - start)
    return hit_rate


if __name__ == "__main__":
    hit_rate_score = fast_eva_recall()

    # 只使用文本召回 准确率 0.911103 耗时18:21
    # 使用 向量召回8个多小时
    # 多进程 文本召回耗时 112.3237s
    # 多线程 耗时
    # hit rate = 0.911103
