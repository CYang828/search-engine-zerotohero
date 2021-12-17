# @Time    : 2021-12-17 19:08
# @Author  : 老赵
# @File    : search.py
from pprint import pprint

from fastapi import APIRouter, Depends

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings

router = APIRouter()


@router.get("", name="search:test")
async def get_all_tags(settings: AppSettings = Depends(get_app_settings)):
    pprint(AppSettings)
    return {
        "app_name": settings.debug,
        "admin_email": 'sss',
        "items_per_user": 'sss',
    }
