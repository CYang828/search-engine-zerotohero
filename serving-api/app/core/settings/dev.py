# @Time    : 2021-12-17 15:54
# @Author  : 老赵
# @File    : dev.py

import logging

from app.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True

    title: str = "Dev FastAPI Search Engine"
    description: str = "开发环境，春阳搜索引擎"

    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env"
        env_file_encoding = 'utf-8'
