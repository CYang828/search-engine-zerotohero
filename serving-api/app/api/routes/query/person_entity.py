# @Time    : 2021-12-20 14:12
# @Author  : 老赵
# @File    : person_entity.py
import happybase
from fastapi import APIRouter
from app.models.schemas.query import PersonResponse

router = APIRouter()


@router.get('/persons/{row_key}', name="query:person", summary='特征工程，person实体搜索', response_model=PersonResponse)
async def persons(row_key: str):
    """
    特征获取API：person实体搜索
    - param row_key: 路径参数：hbase行号，作者的url_token与文章id的拼接
    - return: 是否查询到preson实体
    """
    try:
        connection = happybase.Connection(host="10.30.89.124", port=9090, timeout=None)  # 这里启动接口服务就建立链接，节约每次查询需要的时间
        table = connection.table('document_features')  # table为happybase.table.Table类型
        row_key_data = table.row(row=row_key)
        row_key_data2 = {}
        for k, v in row_key_data.items():
            row_key_data2[k.decode()] = v.decode()
        return {'row_key': row_key, 'row_data': row_key_data2, 'code': 1, 'message': 'success'}
    except Exception as e:
        return {'row_key': row_key, 'row_data': {}, 'code': 0, 'message': str(e)}

