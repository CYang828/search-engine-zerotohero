# @Time    : 2022-01-10 15:03
# @Author  : Li Mengqi
# @File    : feature_extract.py

from fastapi import APIRouter
from app.models.schemas.query import FeatureExtractResonse, SentenceArgs
from app.resources.api_response import ApiResponse, ResponseEnum

router = APIRouter()

@router.get('/extract', name="feature:extract", summary='feature extract', response_model=FeatureExtractResonse)
async def extract(args: SentenceArgs):
    """
    特征提取
    - params: sentence 请求体参数->json
    - return: 暂时愿样子返回
    """

    return ApiResponse.build_success(data={'feature_extract': 'feature extract results {}'.format(args.sentence)})

