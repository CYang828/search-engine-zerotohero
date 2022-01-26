# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 2:26 下午
# @Author  : zhengjiawei
# @FileName: rank.py
# @Software: PyCharm

from app.models.schemas.rwschema import RWSchema

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class RankResponse(RWSchema):
    # term_weight: dict = {}
    rank: str