# @Time    : 2021-12-20 15:07
# @Author  : 老赵
# @File    : query.py
from app.models.common import DateTimeModelMixin, IDModelMixin
from app.models.domain.rwmodel import RWModel


class Person(IDModelMixin, DateTimeModelMixin, RWModel):
    slug: str
    title: str
    description: str
    body: str
    # tags: List[str]
    # author: Profile
    # favorited: bool
    # favorites_count: int
