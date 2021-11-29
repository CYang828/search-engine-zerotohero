##!/usr/bin/python3
# -*- coding:utf-8 -*-
# @Time   :${2021/11/25} ${14:13}
# @Author :Mengqi Li
# @FileName:${NAME}.py

from pymongo import MongoClient
from features_utils import extract_article, hanlp_token_and_ner, split_sentence
import jieba.analyse as analyse
import json
import happybase


class Process:

    def __init__(self, url='mongodb://10.30.89.124:27011/', db='zhihu_new', collection='articles',
                 h_table_name='document_features'):
        """
        :param url:数据库所在服务器的ip和port
        :param db: 数据库名
        :param collection:集合名称
        :param h_table_name:hbase中表的名称
        """
        # 建立mongo的链接
        self.client = MongoClient(url)
        self.collec = self.client[db][collection]
        # 建立hbase的链接
        connection = happybase.Connection(host='10.30.89.124', port=9090)
        table_name_list = connection.tables()
        print('数据库中的表名称', table_name_list)
        if h_table_name.encode() not in table_name_list:  # table_name_list中的表的名字是字节型的，所以h_table_name要encode()成字节型
            # 表不存在，新建表，author、comment、document 是表中的三个族
            families = {
                "author": dict(),
                "comment": dict(),
                "document": dict(),
            }
            connection.create_table(h_table_name, families)  # 创建表格
        self.table = happybase.Table(h_table_name, connection)  # 获取表格对象
        # 获取hbase中已有数据的量，这个值用于从mongo中断点续传数据
        self.sum_row_hbase = 0
        for _ in self.table.scan(columns=['author:gender']):
            self.sum_row_hbase += 1
        print('本次执行之前，hbase中{}表中有{}条数据。'.format(h_table_name, self.sum_row_hbase))

    def get_data_from_mongodb(self):
        """
        :return: 返回的是个Cursor（游标）类型的数据，可以通过迭代的方式取出每一个元素，元素类型是dict
        """
        return self.collec.find(no_cursor_timeout=True, batch_size=10).skip(self.sum_row_hbase)

    def get_author_inf(self, author_data):
        author_faimly = dict()
        author_faimly['author:id'] = str(author_data['uid'])  # 作者id
        author_faimly['author:name'] = author_data['name']  # 作者名字
        author_faimly['author:user_type'] = author_data['user_type']  # 作者类型
        author_faimly['author:description'] = author_data['description']  # 作者简介
        author_faimly['author:is_advertiser'] = str(author_data['is_advertiser'])  # 是否是企业账号
        author_faimly['author:headline'] = author_data['headline']  # 作者的大字标题
        try:
            author_faimly['author:badge'] = json.dumps({'badge': author_data['badge']})  # 作者的徽章
        except Exception as e:
            print('author中不存在badge建')
            print(e)
            author_faimly['author:badge'] = json.dumps({'badge': []})  # 既然没有就赋值为空列表
        author_faimly['author:gender'] = str(author_data['gender'])  # 作者的性别
        author_faimly['author:url'] = author_data['url']  # 作者的主页链接
        author_faimly['author:url_token'] = author_data['url_token']  # 作者主页url唯一标识
        author_faimly['author:avatar_url'] = author_data['avatar_url']  # 作者头像的链接
        return author_faimly

    def get_comment_inf(self, one_data):
        comment_family = dict()
        # comment_count	评论数量
        comment_family['comment:comment_count'] = str(one_data['comment_count'])
        # voteup_count	点赞数量
        comment_family['comment:voteup_count'] = str(one_data['voteup_count'])
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
        comment_family['comment:created_time_list'] = json.dumps({'created_time_list': comment_created_time_list})
        comment_family['comment:content_list'] = json.dumps({'content_list': comment_content_list})
        comment_family['comment:avatar_url_list'] = json.dumps({'avatar_url_list': comment_avatar_url_list})
        comment_family['comment:name_list'] = json.dumps({'name_list': comment_name_list})
        comment_family['comment:url_token_list'] = json.dumps({'url_token_list': comment_url_token_list})
        comment_family['comment:vote_count_list'] = json.dumps({'vote_count_list': comment_vote_count_list})
        return comment_family

    def get_document_inf(self, one_data):
        document_faimly = dict()
        document_faimly['document:title'] = one_data['title']  # title文章标题
        document_faimly['document:content'] = one_data['content']  # content正文内容
        document_faimly['document:excerpt'] = one_data['excerpt']  # excerpt文章前面的若干文字内容
        document_faimly['document:type'] = one_data['type']  # type	文章类型
        document_faimly['document:image_url'] = one_data['image_url']  # image_url文章的封面图片地址链接
        document_faimly['document:created'] = str(one_data['created'])  # created文章创建时间戳
        document_faimly['document:updated'] = str(one_data['updated'])  # updated文章更新时间戳
        document_faimly['document:id'] = str(one_data['id'])  # id知乎编码的文章id
        document_faimly['document:has_column'] = str(one_data['has_column'])  # has_column专栏收录
        # tokens	文章的分词结果
        # entity	文章中出现的人名、地名、机构名等
        clean_content = extract_article(one_data['content'])
        if clean_content.strip() == '':
            document_faimly['document:tokens'] = json.dumps({'tok_fine': []})
            document_faimly['document:entity'] = json.dumps({})
            document_faimly['document:top5words'] = json.dumps({'top5word': []})
            print('文章内容是空:', document_faimly)
            return document_faimly
        try:
            document_tokens, document_entity = hanlp_token_and_ner(clean_content,
                                                                   use_split_sentence=False)  # 使用hanlp工具进行分词和实体识别
            document_top5words = analyse.textrank(clean_content, topK=5, withWeight=False,
                                                  allowPOS=('ns', 'n', 'vn', 'v'))  # 从ns地名，n名词，vn名动词， v动词这些词性中提取关键词
            document_faimly['document:tokens'] = document_tokens
            document_faimly['document:entity'] = document_entity
            document_faimly['document:top5words'] = json.dumps({'top5word': document_top5words})
        except Exception as e:
            print('分词 or 实体识别 or top5w时出错')
            print(e)
            document_faimly['document:tokens'] = json.dumps({'tok_fine': []})
            document_faimly['document:entity'] = json.dumps({})
            document_faimly['document:top5words'] = json.dumps({'top5word': []})
        return document_faimly

    def insert_hbase(self, row_data):
        # print(row_data['author:url_token'] + '_' + str(row_data['document:id']))
        self.table.put(row_data['author:url_token'] + '_' + str(row_data['document:id']),
                       row_data)  # 在row1行,cf:1列插入值1 table.put("row1",{"cf:1":"1"})

    def forward(self):
        num_of_into_hbase = 0
        for one_data in self.get_data_from_mongodb():
            # author Column family
            author_family = self.get_author_inf(one_data['author'])
            # comment Column family
            comment_family = self.get_comment_inf(one_data)
            # document Column family
            document_faimly = self.get_document_inf(one_data)
            row_data = {**author_family, **comment_family, **document_faimly}  # 把三个字典合并为一个
            self.insert_hbase(row_data)
            num_of_into_hbase += 1
        print('本次从mongodb一共转移{}条数据到hbase'.format(num_of_into_hbase))


if __name__ == '__main__':
    process = Process()
    process.forward()
