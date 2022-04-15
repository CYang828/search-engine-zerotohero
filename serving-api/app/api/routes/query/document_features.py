# @Time    : 2021-12-20 14:12
# @Author  : 老赵
# @File    : document_features.py
import happybase
from fastapi import APIRouter
from app.models.schemas.query import PersonResponse
from app.resources.api_response import ApiResponse, ResponseEnum

router = APIRouter()


@router.get(
    "/document/{row_key}",
    name="query:document",
    summary="特征工程，文章特征",
    response_model=PersonResponse,
)
async def document(row_key: str):
    """
    特征获取API：person实体搜索
    - param row_key: 路径参数：hbase行号，作者的url_token与文章id的拼接
    - return: 是否查询到preson实体
    """
    try:
        connection = happybase.Connection(host="10.30.89.124", port=9090, timeout=None)
        table = connection.table("document_features_test3")
        row_key_data = table.row(row=row_key)
        row_key_data2 = {}
        for k, v in row_key_data.items():
            row_key_data2[k.decode()] = v.decode()
        return ApiResponse.build_success(
            data={"row_key": row_key, "row_data": row_key_data2}
        )
        # return {'row_key': row_key, 'row_data': row_key_data2, 'code': 1, 'message': 'success'}
    except Exception as e:
        # return {'row_key': row_key, 'row_data': {}, 'code': 0, 'message': str(e)}
        return ApiResponse.build_error(ResponseEnum.HBASE_CONN_ERROR)
