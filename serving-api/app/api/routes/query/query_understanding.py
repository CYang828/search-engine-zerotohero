# @Time    : 2022-01-10 15:03
# @Author  : 老赵
# @File    : term_weight.py

from fastapi import APIRouter
from app.models.schemas.query import QueryUnderstandingResonse, SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum

router = APIRouter()

@router.get('/understanding', name="query:understanding", summary='query understanding', response_model=QueryUnderstandingResonse)
async def understanding(args: SentenceArgs):
    """
    query 理解
    - params: sentence 请求体参数->json
    - return: 暂时愿样子返回
    """
    return ApiResponse.build_success(data={'query_understand': 'query understanding results {}'.format(args.sentence)})

