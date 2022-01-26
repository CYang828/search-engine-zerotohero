# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 2:56 下午
# @Author  : zhengjiawei
# @FileName: rerank.py
# @Software: PyCharm

from app.models.schemas.rank import RankResponse
from app.models.schemas.query import SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum
from app.services.rerank import ReRank
from fastapi import APIRouter


router = APIRouter()


@router.get('/rerank', name="rerank", summary='重排策略', response_model=RankResponse)
async def rerank():
    """
    排序算法，对精排结果进行重排
    - return: result_rerank
    """
    try:
        # rerank
        result_rerank = ReRank().se_rank()

        return ApiResponse.build_success(data={'result_rerank': result_rerank})
    except Exception as e:

        return ApiResponse.build_error(ResponseEnum.RERANK_PROCESS_ERROR)