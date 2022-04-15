# -*- coding:utf-8 -*-
# @Time   :2022/3/30 6:46 下午
# @Author :Li Meng qi
# @FileName:extract_searchinfo.py
from extract_entity import BaseExtract
from entity.searchinfo import SearchInfo
import json


class ExtractSearchInfo(BaseExtract):
    def __init__(self):
        pass

    def extract(self, row_data):
        searchinfo = SearchInfo()
        # userid  document_id      search_token  click  like  comment
        searchinfo.userid = str(row_data[1])
        searchinfo.document_id = str(row_data[2])
        searchinfo.search_token = row_data[3]
        searchinfo.click = str(row_data[4])
        searchinfo.like = str(row_data[5])
        searchinfo.comment = str(row_data[6])
        return searchinfo
