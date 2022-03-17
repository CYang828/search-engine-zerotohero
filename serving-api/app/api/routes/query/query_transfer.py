# @Time    : 2022-01-10 15:03
# @Author  : Li Mengqi
# @File    : query_transfer.py

from fastapi import APIRouter
from app.models.schemas.query import QueryTransferResonse, SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum

router = APIRouter()


@router.get('/transfer', name="query:transfer", summary='query transfer', response_model=QueryTransferResonse)
async def transfer(args: SentenceArgs):
    """
    query transfer
    - params: sentence 请求体参数->json
    - return: 暂时愿样子返回
    """
    return ApiResponse.build_success(data={'query_understand': 'query transfer results {}'.format(args.sentence)})
