# @Time    : 2021-12-17 15:54
# @Author  : 老赵
# @File    : dev.py

import logging

from app.core.settings.app import AppSettings


class DevAppSettings(AppSettings):
    debug: bool = True

    title: str = "Dev FastAPI Search Engine"
    description: str = "开发环境，春阳搜索引擎"
    contact: dict = {
        "name": "Search Engine Group",
        "url": "http://39.106.195.80:15002/",
        "email": "zhao_xingrong@163.com",
    }
    logging_level: int = logging.DEBUG

    class Config(AppSettings.Config):
        env_file = ".env"
        env_file_encoding = 'utf-8'
