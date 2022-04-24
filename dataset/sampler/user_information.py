# -*- coding: utf-8 -*-
# @Time    : 2022/3/18 10:42 上午
# @Author  : zhengjiawei
# @FileName: user_information.py
# @Software: PyCharm
import random

import numpy as np
import pandas as pd

from dataset.sampler.utils import generate_userid, random_seed, BaseSampler

random_seed(2022)


class UserSampler(BaseSampler):
    age_dic = {1: "19岁以下", 2: "20-29岁之间", 3: "30-39岁之间", 4: "其他"}
    education_dic = {1: "专科及以下", 2: "本科", 3: "硕士", 4: "博士", 5: "其他"}
    gender_dic = {1: "男", 0: "女"}
    cities = [
        "北京",
        "深圳",
        "上海",
        "广州",
        "天津",
        "重庆",
        "南宁",
        "拉萨",
        "银川",
        "乌鲁木齐",
        "呼和浩特",
        "香港",
        "澳门",
        "台北",
        "济南",
        "石家庄",
        "长春",
        "哈尔滨",
        "沈阳",
        "兰州",
        "太原",
        "西安",
        "郑州",
        "合肥",
        "南京",
        "杭州",
        "福州",
        "南昌",
        "海口",
        "贵阳",
        "长沙",
        "武汉",
        "成都",
        "昆明",
        "西宁",
        "其他",
    ]

    cities_dic = {i + 1: each for i, each in enumerate(cities)}
    jobs = [
        "学生",
        "产品经理",
        "自由职业",
        "程序员",
        "工程师",
        "设计师",
        "腾讯",
        "教师",
        "人力资源（HR)",
        "运营",
        "律师",
        "其他",
    ]
    jobs_dic = {i + 1: each for i, each in enumerate(jobs)}

    def __init__(self):
        super().__init__()
        self.userid_list = generate_userid(self.user_nums)
        self.gender_list = self.sample_gender()
        self.age_list = self.sample_age()
        self.city_list = self.sample_city()
        self.job_list = self.sample_job()
        self.education_list = self.sample_education()

    def sample(self):
        user_data = pd.DataFrame()
        user_data.loc[:, "userid"] = self.userid_list
        user_data.loc[:, "gender"] = self.gender_list
        user_data.loc[:, "age"] = self.age_list
        user_data.loc[:, "city"] = self.city_list
        user_data.loc[:, "job"] = self.job_list
        user_data.loc[:, "education"] = self.education_list
        # 修正数据 19岁以下只能是学生或者其他，education不能是硕士或者博士学历
        for i in range(user_data.shape[0]):
            education = user_data.loc[i, "education"]
            if education in [3, 4]:
                education = random.sample([1, 2, 5], 1)[0]
            user_data.loc[i, "education"] = education

        user_origin_data = pd.DataFrame()
        user_origin_data.loc[:, "userid"] = user_data.loc[:, "userid"]
        # 获得未转换的数据
        for i in range(user_data.shape[0]):
<<<<<<< HEAD
            user_origin_data.loc[i, 'gender'] = self.gender_dic[user_data.loc[i, 'gender']]
            user_origin_data.loc[i, 'age'] = user_data.loc[i, 'age']
            user_origin_data.loc[i, 'city'] = self.cities_dic[user_data.loc[i, 'city']]
            user_origin_data.loc[i, 'job'] = self.jobs_dic[user_data.loc[i, 'job']]
            user_origin_data.loc[i, 'education'] = self.education_dic[user_data.loc[i, 'education']]
        user_data.to_csv(self.sampler_configs['data_path'] + 'user_data.csv', index=False)
        user_origin_data.to_csv(self.sampler_configs['data_path'] + 'user_origin_data.csv', index=False)
=======
            user_origin_data.loc[i, "gender"] = self.gender_dic[
                user_data.loc[i, "gender"]
            ]
            user_origin_data.loc[i, "age"] = self.age_dic[user_data.loc[i, "age"]]
            user_origin_data.loc[i, "city"] = self.cities_dic[user_data.loc[i, "city"]]
            user_origin_data.loc[i, "job"] = self.jobs_dic[user_data.loc[i, "job"]]
            user_origin_data.loc[i, "education"] = self.education_dic[
                user_data.loc[i, "education"]
            ]
        user_data.to_csv(
            self.sampler_configs["data_path"] + "user_data.csv", index=False
        )
        user_origin_data.to_csv(
            self.sampler_configs["data_path"] + "user_origin_data.csv", index=False
        )
>>>>>>> 2b9df2d699a7843e3370401f199a048730122da9

    def sample_gender(self) -> list:
        """
        模拟知乎男女用户占比，男性用户占67%，女生用户占比33%
        :return gender_list:列表中1表示男性，0 表示女性
        """
        gender_array = np.random.binomial(1, 0.67, self.user_nums)
        gender_list = list(gender_array)
        random.shuffle(gender_list)
        return gender_list

    def sample_age(self) -> list:
        """
        {1:'19岁以下',2:'20-29岁之间',3:'30-39岁之间',4:'其他'}
        19岁以下占比 20%，20-29岁之间 占比70%，30-39岁之间 占比9%， 其他占比1%
        :return: age_list
        """

        # age_dic = {1: '19岁以下', 2: '20-29岁之间', 3: '30-39岁之间', 4: '其他'}
        age_list = (
            ["1"] * int(self.user_nums * 0.2)
            + ["2"] * int(self.user_nums * 0.7)
            + ["3"] * int(self.user_nums * 0.09)
            + ["4"] * int(self.user_nums * 0.01)
        )
        age_list = [int(each) for each in age_list]
        random.shuffle(age_list)

        return age_list

    def sample_education(self):
        """
        education_dic = {1:'专科及以下',2:'本科',3:'硕士',4:'博士',5:其他}
        :return
        """
        education_list = list(np.random.normal(2, 1, self.user_nums))
        education_list = np.ceil(education_list)
        for i, each in enumerate(education_list):
            while each not in [1, 2, 3, 4, 5]:
                each = np.ceil(np.random.normal(2, 1))
            education_list[i] = each
        random.shuffle(education_list)
        return education_list

    def sample_city(self) -> list:
        # '北上广深' 60%，其他省市39%，1% 其他
        one_or_zero = np.random.binomial(1, 0.6, self.user_nums)
        one_list = [np.random.randint(1, 5) for each in one_or_zero if each == 1]
        zero_list = [
            np.random.randint(5, len(self.cities)) for each in one_or_zero if each == 0
        ]
        cities_list = []
        for each in zero_list:
            if np.random.binomial(1, 0.025):
                cities_list.append(len(self.cities))
            else:
                cities_list.append(each)

        cities_list.extend(one_list)
        random.shuffle(cities_list)
        return cities_list

    def sample_job(self):
        """
        学生比例 40% 其他行业总共占58%,其他 占3.3%
        :return
        """

        one_or_zero = np.random.binomial(1, 0.4, self.user_nums)
        one_list = [1 for each in one_or_zero if each == 1]
        zero_list = [
            np.random.randint(2, len(self.jobs)) for each in one_or_zero if each == 0
        ]
        jobs_list = []
        for each in zero_list:
            if np.random.binomial(1, 0.033):
                jobs_list.append(len(self.jobs))
            else:
                jobs_list.append(each)
        jobs_list.extend(one_list)
        random.shuffle(jobs_list)
        return jobs_list


if __name__ == "__main__":
    UserSampler().sample()
