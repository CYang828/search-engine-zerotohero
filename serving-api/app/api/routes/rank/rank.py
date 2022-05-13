# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 2:22 下午
# @Author  : zhengjiawei
# @FileName: rank.py
# @Software: PyCharm


from app.models.schemas.rank import RankResponse
from app.models.schemas.query import SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum
from app.services.rank import Rank
from fastapi import APIRouter
from ranker.src.test import main


router = APIRouter()


@router.get("/rank", name="rank", summary="排序策略", response_model=RankResponse)
async def rank():
    """
    排序算法，对召回结果进行精排
    - return: result_rank
    """
    try:
        # rank
        result_rank = Rank().main()

        return ApiResponse.build_success(data={"result_rank": result_rank})
    except Exception as e:

        return ApiResponse.build_error(ResponseEnum.RANK_PROCESS_ERROR)
