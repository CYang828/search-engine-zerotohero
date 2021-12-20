# @Time    : 2021-12-20 16:03
# @Author  : 老赵
# @File    : api_response.py
from enum import Enum

from fastapi.responses import ORJSONResponse


class ResponseEnum(Enum):
    SUCCESS = {'msg': "成功", 'code': "10000"}
    METHOD_ARGS_ERROR = {'msg': "参数不正确", 'code': "40000"}
    HBASE_CONN_ERROR = {'msg': "hbase连接失败", 'code': "40009"}

    def get_msg(self) -> str:
        return self.value['msg']

    def get_code(self) -> str:
        return self.value['code']


class ApiResponse:
    @staticmethod
    def build_success(data: any = None):
        content = {
            "code": ResponseEnum.SUCCESS.get_code(),
            "msg": ResponseEnum.SUCCESS.get_msg()
        }
        if data:
            content['data'] = data
        return ORJSONResponse(content=content, status_code=200)

    @staticmethod
    def build_error(response_enum: ResponseEnum = ResponseEnum.SUCCESS):
        content = {
            "code": response_enum.get_code(),
            "msg": response_enum.get_msg()
        }
        return ORJSONResponse(content=content, status_code=200)
