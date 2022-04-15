# -*- coding:utf-8 -*-
# @Time   :2022/2/28 5:08 下午
# @user :Li Meng qi
# @FileName:extract_user.py
from extract_entity import BaseExtract
from entity.user import User
import json


class ExtractUser(BaseExtract):
    def __init__(self):
        # self.user = user()
        pass

    def extract(self, row_data):
        user = User()
        # userid	gender	age	city	job	education
        user.userid = str(row_data[0])
        user.gender = str(row_data[1])
        user.age = str(row_data[2])
        user.city = str(row_data[3])
        user.job = str(row_data[4])
        user.education = str(row_data[5])
        return user
