# @Time    : 2021-12-20 15:04
# @Author  : 老赵
# @File    : query.py
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.domain.query import Person

from app.models.schemas.rwschema import RWSchema

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class PersonForResponse(RWSchema, Person):
    tags: List[str] = Field(..., alias="tagList")


class PersonInResponse(RWSchema):
    article: PersonForResponse


class PersonResponse(RWSchema):
    row_key: str
    row_data: dict = {}


class SentenceArgs(RWSchema):
    sentence: str


class QueryProcessingArgs(RWSchema):
    sentence: str
    process_type: str


class AssociateArgs(RWSchema):
    sentence: str
    client_type: str


class TermResponse(RWSchema):
    # term_weight: dict = {}
    term_weight: list


# query understanding response
class QueryProcessingResonse(RWSchema):
    query_processing: str


# feature extract
class FeatureExtractResonse(RWSchema):
    feature_extract: dict


# query transfer
class QueryTransferResonse(RWSchema):
    query_transfer: dict


# query association
class AssociationResponse(RWSchema):
    query_association: list


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
