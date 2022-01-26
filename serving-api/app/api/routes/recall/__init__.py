# -*- coding: utf-8 -*-
# @Time    : 2022/1/25 10:46 上午
# @Author  : zhengjiawei
# @FileName: __init__.py.py
# @Software: PyCharm

from fastapi import APIRouter

from app.api.routes.recall import recall

router = APIRouter()
router.include_router(recall.router, prefix="/analysis")

