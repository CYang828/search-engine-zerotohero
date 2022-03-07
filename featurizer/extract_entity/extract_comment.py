# -*- coding:utf-8 -*-
# @Time   :2022/2/28 5:08 下午
# @Author :Li Meng qi
# @FileName:extract_comment.py
from extract_entity import BaseExtract
from entity.comment import Comment
import json


class ExtractComment(BaseExtract):
    def __init__(self):
        self.comment = Comment()

    def extract(self, row_data):
        one_data = row_data
        comment_family = dict()
        # comment_count	评论数量
        self.comment.comment_count = str(one_data['comment_count'])
        # voteup_count	点赞数量
        self.comment.voteup_count = str(one_data['voteup_count'])
        # 以下新建的列表中相同index位置对应同一条评论的属性
        # created_time	评论创建时间
        comment_created_time_list = []
        # content	评论内容
        comment_content_list = []
        # avatar_url  评论作者头像图片链接
        comment_avatar_url_list = []
        # name	评论作者名字
        comment_name_list = []
        # url_token	评论作者主页url唯一标识
        comment_url_token_list = []
        # vote_count 评论点赞
        comment_vote_count_list = []
        for one_comment in one_data['comments']:
            comment_created_time_list.append(one_comment['created_time'])
            comment_content_list.append(one_comment['content'])
            comment_avatar_url_list.append(one_comment['author']['member']['avatar_url'])
            comment_name_list.append(one_comment['author']['member']['name'])
            comment_url_token_list.append(one_comment['author']['member']['url_token'])
            comment_vote_count_list.append(one_comment['vote_count'])
        self.comment.created_time_list = json.dumps({'created_time_list': comment_created_time_list})
        self.comment.content_list = json.dumps({'content_list': comment_content_list})
        self.comment.avatar_url_list = json.dumps({'avatar_url_list': comment_avatar_url_list})
        self.comment.name_list = json.dumps({'name_list': comment_name_list})
        self.comment.url_token_list = json.dumps({'url_token_list': comment_url_token_list})
        self.comment.vote_count_list = json.dumps({'vote_count_list': comment_vote_count_list})
        return self.comment
