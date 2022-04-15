# -*- coding:utf-8 -*-
# @Time   :2022/2/24 5:21 下午
# @Author :Li Meng qi
# @FileName:clean_html_tag.py
from feature_utils import FeatureBase
from bs4 import BeautifulSoup as bs


class CleanHtmlTag(FeatureBase):
    def run(self, data):
        if isinstance(data, float):
            print(data)
            return ""
        result = bs(data).get_text()
        return result
