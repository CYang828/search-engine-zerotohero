# -*- coding: utf-8 -*-
# @Time    : 2022/2/28 9:04 下午
# @Author  : zhengjiawei
# @FileName: utils.py
# @Software: PyCharm


def get_query_json(query, boost_title=3, boost_summary=2, boost_content=1):
    query_json = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "title": {
                                "query": query,
                                "boost": boost_title
                            }
                        }
                    },
                    {
                        "match": {
                            "content": {
                                "query": query,
                                "boost": boost_content
                            }
                        }
                    }
                    , {
                        "match": {
                            "excerpt": {
                                "query": query,
                                "boost": boost_summary
                            }
                        }

                    }
                ]
            }
        }
    }
    return query_json


def parse_es_content(query_dict):
    ids_list = []
    query_list = query_dict['hits']['hits']
    length = len(query_list)
    for i in range(length):
        id = query_list[i]['_source']['id']
        ids_list.append(id)
    return ids_list
