# @Time    : 2021-12-17 15:54
# @Author  : 老赵
# @File    : prod.py

from app.core.settings.app import AppSettings


class ProdAppSettings(AppSettings):
    class Config(AppSettings.Config):
        env_file = "prod.env"
