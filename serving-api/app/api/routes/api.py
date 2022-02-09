# @Time    : 2021-12-17 18:52
# @Author  : 老赵
# @File    : api.py
from fastapi import APIRouter

# from app.api.routes import authentication, comments, profiles, tags, users
# from app.api.routes.articles import api as articles
from app.api.routes import search, index, query, feature, recall, rank, rerank

router = APIRouter()
# router.include_router(authentication.router, tags=["authentication"], prefix="/users")
# router.include_router(users.router, tags=["users"], prefix="/user")
# router.include_router(profiles.router, tags=["profiles"], prefix="/profiles")
router.include_router(index.router, tags=["index"], prefix="")
# router.include_router(
#     comments.router,
#     tags=["comments"],
#     prefix="/articles/{slug}/comments",
# )
router.include_router(search.router, tags=["search"], prefix="/search")
router.include_router(query.router, tags=["query"], prefix="/query")
router.include_router(recall.router, tags=["recall"], prefix="/recall")
router.include_router(rank.router, tags=["rank"], prefix="/rank")
router.include_router(rerank.router, tags=["rerank"], prefix="/rerank")

router.include_router(feature.router, tags=["feature"], prefix="/feature")
