# @Time    : 2021-12-20 14:11
# @Author  : 老赵
# @File    : __init__.py.py
from fastapi import APIRouter

from app.api.routes.query import (
    document_features,
    term_weight,
    query_association,
    query_processing,
)

router = APIRouter()

router.include_router(document_features.router, prefix="/features")
router.include_router(term_weight.router, prefix="/features")

# query processing
router.include_router(query_processing.router, prefix="")
# query association
router.include_router(query_association.router, prefix="")
