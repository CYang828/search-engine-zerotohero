# -*- coding:utf-8 -*-
# @Time   :2022/2/24 11:21 上午
# @Author :Li Meng qi
# @FileName:run_build_features.py
from pymongo import MongoClient
import happybase
import os
from extract_entity.extract_author import ExtractAuthor
from extract_entity.extract_comment import ExtractComment
from extract_entity.extract_document import ExtractDocument

os.environ["CUDA_VISIBLE_DEVICES"] = '1,2,3'


class Processer:

    def __init__(self, **kwargs):
        self.connect(kwargs)
        # 处理
        self.extract_author = ExtractAuthor()
        self.extract_comment = ExtractComment()
        self.extract_document = ExtractDocument()

    def connect(self, kwargs):
        # 建立mongo的链接
        self.client = MongoClient(kwargs['url'])
        self.collec = self.client[kwargs['db']][kwargs['collection']]
        # 建立hbase的链接
        self.connection = happybase.Connection(host='10.30.89.124', port=9090)
        table_name_list = self.connection.tables()
        print('数据库中的表名称', table_name_list)
        h_table_name = kwargs['h_table_name']
        if h_table_name.encode() not in table_name_list:  # table_name_list中的表的名字是字节型的，所以h_table_name要encode()成字节型
            # 表不存在，新建表，author、comment、document 是表中的三个族
            families = {
                "author": dict(),
                "comment": dict(),
                "document": dict(),
            }
            self.connection.create_table(h_table_name, families)  # 创建表格
        self.table = happybase.Table(h_table_name, self.connection)  # 获取表格对象
        # 获取hbase中已有数据的量，这个值用于从mongo中断点续传数据
        self.sum_row_hbase = 0
        for _ in self.table.scan(columns=['author:gender']):
            self.sum_row_hbase += 1
        print('本次执行之前，hbase中{}表中有{}条数据。'.format(h_table_name, self.sum_row_hbase))

    def load_from_mongo(self):
        """
        :return: 返回的是个Cursor（游标）类型的数据，可以通过迭代的方式取出每一个元素，元素类型是dict
        """
        return self.collec.find(no_cursor_timeout=True, batch_size=10).skip(self.sum_row_hbase)

    def build_entity(self, one_data):
        author = self.extract_author.extract(one_data)
        comment = self.extract_comment.extract(one_data)
        document = self.extract_document.extract(one_data)
        return author, comment, document

    def merge(self, author, comment, document):
        author_family = {'author:' + key: value for key, value in author.__dict__.items()}
        comment_family = {'comment:' + key: value for key, value in comment.__dict__.items()}
        document_family = {'document:' + key: value for key, value in document.__dict__.items()}
        return {**author_family, **comment_family, **document_family}

    def insert_hbase(self, row_data):
        self.table.put(row_data['author:url_token'] + '_' + str(row_data['document:id']),
                       row_data)

    def run(self):
        num_of_into_hbase = 0
        for one_data in self.load_from_mongo():
            author, comment, document = self.build_entity(one_data)
            row_data = self.merge(author, comment, document)
            self.insert_hbase(row_data)
            num_of_into_hbase += 1
            if num_of_into_hbase % 50 == 0:
                print(num_of_into_hbase)
        print('本次从mongodb一共转移{}条数据到hbase'.format(num_of_into_hbase))
        self.close()

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    process = Processer(url='mongodb://10.30.89.124:27013/', db='zhihu_new', collection='articles',
                        h_table_name='document_features_03')
    process.run()
