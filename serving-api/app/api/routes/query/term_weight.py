# @Time    : 2022-01-10 15:03
# @Author  : 老赵
# @File    : term_weight.py

import happybase
import jieba
from fastapi import APIRouter
from app.models.schemas.query import TermResponse, SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum
from app.services.term_anlyze import TermAnalyze

router = APIRouter()


@router.get('/term', name="query:term", summary='特征工程，term分析', response_model=TermResponse)
async def term(args: SentenceArgs):
    """

    - return:
    """
    # 获取请求参数 json， sentence
    sentence = args.sentence

    # 分词 query_list # todo  query改写预处理
    query_list = jieba.cut(sentence)

    # query_weight
    query_weight = TermAnalyze(query_list=query_list).get_term_weight()

    return ApiResponse.build_success(data={'term_weight': [float(i) for i in query_weight]})
