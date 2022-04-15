# @Time    : 2021-12-20 12:26
# @Author  : 老赵
# @File    : index.py
from fastapi import APIRouter, Depends

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings

router = APIRouter()


@router.get("/", name="index")
async def index(settings: AppSettings = Depends(get_app_settings)):
    return {
        "app_name": settings.debug,
        "admin_email": "sss",
        "items_per_user": "sss",
    }
