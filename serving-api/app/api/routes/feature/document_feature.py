# @Time    : 2021-12-20 14:12
# @Author  : 老赵
# @File    : document_feature.py
import happybase
from fastapi import APIRouter
from app.models.schemas.query import DocumentResponse
from app.resources.api_response import ApiResponse, ResponseEnum
from featurizer.feature_api.document import DocumentFeature

from loader import load_configs

configs = load_configs(func='document_feature_api')
router = APIRouter()


@router.get(
    "/document/{row_key}",
    name="feature:document",
    summary="从hbase平台中调用相关document特征",
    response_model=DocumentResponse,
)
async def document(row_key: str):
    """
    从hbase中获取document相关的一系列特征
    - param row_key: 路径参数：hbase行号，作者的url_token与文章id的拼接
    - return: 查询正确返回查询到的结果，查询失败返回错误信息
    """
    try:
        docf = DocumentFeature(**configs)
        row_key_data = docf.get(row_key=row_key)
        docf.close()
        return ApiResponse.build_success(
            data={"row_key": row_key, "row_data": row_key_data}
        )
        # return {'row_key': row_key, 'row_data': row_key_data2, 'code': 1, 'message': 'success'}
    except Exception as e:
        print(e.__str__())
        # return {'row_key': row_key, 'row_data': {}, 'code': 0, 'message': str(e)}
        return ApiResponse.build_error(ResponseEnum.HBASE_CONN_ERROR)
