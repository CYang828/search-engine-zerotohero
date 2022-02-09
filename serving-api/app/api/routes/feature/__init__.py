# -*- coding:utf-8 -*-
# @Time   :2022/1/27 2:55 下午
# @Author :Li Meng qi
# @FileName:__init__.py.py
from fastapi import APIRouter

from app.api.routes.feature import document_feature

router = APIRouter()
router.include_router(document_feature.router, prefix="")
