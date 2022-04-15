# @Time    : 2021-12-17 15:50
# @Author  : 老赵
# @File    : __init__.py

from enum import Enum

from pydantic import BaseSettings


class AppEnvTypes(Enum):
    """枚举型设计 不同环境对应的环境字符串"""

    prod: str = "prod"
    dev: str = "dev"
    test: str = "test"


class BaseAppSettings(BaseSettings):
    """基类app配置，设置默认类属性为生产环境"""

    app_env: AppEnvTypes = AppEnvTypes.dev

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
