# @Time    : 2021-12-20 14:11
# @Author  : 老赵
# @File    : __init__.py.py
from fastapi import APIRouter

from app.api.routes.query import term_weight, query_understanding, feature_extract, query_transfer

router = APIRouter()


router.include_router(term_weight.router, prefix="/features")

# query understanding
router.include_router(query_understanding.router, prefix="")
# feature extract
router.include_router(feature_extract.router, prefix="/features")
# query transfer
router.include_router(query_transfer.router, prefix="")