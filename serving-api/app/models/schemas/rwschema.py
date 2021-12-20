# @Time    : 2021-12-20 15:14
# @Author  : 老赵
# @File    : rwschema.py
from app.models.domain.rwmodel import RWModel


class RWSchema(RWModel):
    class Config(RWModel.Config):
        orm_mode = True
