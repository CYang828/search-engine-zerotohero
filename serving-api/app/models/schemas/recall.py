# @Time    : 2022-1-25 10:04
# @Author  : zhengjiawei
# @File    : recall.py

from app.models.domain.query import Person

from app.models.schemas.rwschema import RWSchema

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class RecallResponse(RWSchema):
    # term_weight: dict = {}
    recall: str

# class ArticleInCreate(RWSchema):
#     title: str
#     description: str
#     body: str
#     tags: List[str] = Field([], alias="tagList")
#
#
# class ArticleInUpdate(RWSchema):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     body: Optional[str] = None
#
#
# class ListOfArticlesInResponse(RWSchema):
#     articles: List[ArticleForResponse]
#     articles_count: int
#
#
# class ArticlesFilters(BaseModel):
#     tag: Optional[str] = None
#     author: Optional[str] = None
#     favorited: Optional[str] = None
#     limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
#     offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)
