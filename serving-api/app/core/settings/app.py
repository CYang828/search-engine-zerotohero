# @Time    : 2021-12-17 15:51
# @Author  : 老赵
# @File    : app.py
import logging
import sys
from typing import Any, Dict, List, Tuple

from loguru import logger

from app.core.loggings import InterceptHandler
from app.core.settings.base import BaseAppSettings
from pydantic import PostgresDsn, SecretStr


class AppSettings(BaseAppSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Search Engine"
    description: str = "描述"
    version: str = "0.0.1"
    contact: dict
    database_url: PostgresDsn
    max_connection_count: int = 10
    min_connection_count: int = 10
    license_info: dict = {
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
    secret_key: SecretStr
    x_logo: dict = {"url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"}
    api_prefix: str = "/api"

    jwt_token_prefix: str = "Token"

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "contact": self.contact,
            "license_info": self.license_info,
            "description": self.description,
            "version": self.version,
            "x_logo": self.x_logo,
        }

    def configure_logging(self) -> None:
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]

        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])
