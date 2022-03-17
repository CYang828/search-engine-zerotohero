# -*- coding: utf-8 -*-
# @Time    : 2022/1/25 10:48 上午
# @Author  : zhengjiawei
# @FileName: main.py
# @Software: PyCharm

from app.models.schemas.recall import RecallResponse
from app.models.schemas.query import SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum
from app.services.recall import ReCall
from fastapi import APIRouter
import jieba

router = APIRouter()


@router.get('/recall', name="recall:recall", summary='召回策略', response_model=RecallResponse)
async def recall(args: SentenceArgs):
    """
    Term分析API，term重要性分析
    - params: sentence 请求体参数->json
    - return: term_weight
    """
    # 获取请求参数 json， sentence
    sentence = args.sentence

    # 分词 query_list # todo  query改写预处理
    query_list = jieba.cut(sentence)
    try:
        # query_weight
        result_recall = ReCall(query_list=query_list).structured_recall()

        return ApiResponse.build_success(data={'result_recall': result_recall})
    except Exception as e:

        return ApiResponse.build_error(ResponseEnum.RECALL_PROCESS_ERROR)
