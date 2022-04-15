# @Time    : 2021-12-20 14:12
# @Author  : 老赵
# @File    : document_feature.py
import happybase
from fastapi import APIRouter
from app.models.schemas.query import DocumentResponse
from app.resources.api_response import ApiResponse, ResponseEnum

router = APIRouter()


@router.get(
    "/document/{row_key}",
    name="feature:document",
    summary="从hbase平台中调用相关document特征",
    response_model=DocumentResponse,
)
async def persons(row_key: str):
    """
    从hbase中获取document相关的一系列特征
    - param row_key: 路径参数：hbase行号，作者的url_token与文章id的拼接
    - return: 查询正确返回查询到的结果，查询失败返回错误信息
    """
    try:
        connection = happybase.Connection(
            host="10.30.89.124", port=9090, timeout=None
        )  # 这里启动接口服务就建立链接，节约每次查询需要的时间
        table = connection.table("document_features")  # table为happybase.table.Table类型
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
