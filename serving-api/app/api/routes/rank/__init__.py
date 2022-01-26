# -*- coding: utf-8 -*-
# @Time    : 2022/1/25 2:45 下午
# @Author  : zhengjiawei
# @FileName: __init__.py.py
# @Software: PyCharm

from fastapi import APIRouter

from app.api.routes.rank import rank

router = APIRouter()
router.include_router(rank.router, prefix="/analysis")