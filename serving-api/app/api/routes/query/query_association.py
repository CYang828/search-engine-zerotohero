# -*- coding:utf-8 -*-
# @Time   :2022/4/12 3:39 下午
# @Author :Li Meng qi
# @FileName:query_association.py
from fastapi import APIRouter
from app.models.schemas.query import AssociationResponse, AssociateArgs
from app.resources.api_response import ApiResponse, ResponseEnum
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# /Users/lmq/Desktop/search-engine-zerotohero/serving-api/app/api/routes
BASE_DIR = BASE_DIR.split("/")[:-4]
BASE_DIR = "/".join(BASE_DIR)
sys.path.append(BASE_DIR)
from query.association import QueryAssociate

router = APIRouter()
query_association = QueryAssociate()


@router.get(
    "/associate",
    name="query:associate",
    summary="query association",
    response_model=AssociationResponse,
)
async def associate(args: AssociateArgs):
    """

    :param args:
    :return:
    """
    sentence = args.sentence
    if not sentence:
        return ApiResponse.build_error(ResponseEnum.QUERY_ASSOCIATION_ERROR)
    if args.client_type == "mobile":
        limit = 4
    elif args.client_type == "pc":
        limit = 7
    else:
        limit = 7
    results = []
    try:
        for key, node in query_association.search(sentence, limit=limit):
            results.append(key)
    except Exception as e:
        return ApiResponse.build_error(ResponseEnum.QUERY_ASSOCIATION_ERROR)
    return ApiResponse.build_success(data={"query_associate": results})
