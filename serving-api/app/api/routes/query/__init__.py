# @Time    : 2021-12-20 14:11
# @Author  : 老赵
# @File    : __init__.py.py
from fastapi import APIRouter

from app.api.routes.query import person_entity

router = APIRouter()

router.include_router(person_entity.router, prefix="/features")
