# -*- coding:utf-8 -*-
# @Time   :2022/4/2 10:45 上午
# @Author :Li Meng qi
# @FileName:test4.py
import time
from multiprocessing import Process, Queue
from pymongo import MongoClient
import happybase
from extract_entity.extract_author import ExtractAuthor
from extract_entity.extract_comment import ExtractComment
from extract_entity.extract_document import ExtractDocument
from feature_utils.text_vector import TextVector
from feature_utils.hanlp_tokens_ner import HanlpTokensNer
import hanlp



class Producer(Process):
    def __init__(self, **kwargs):
        Process.__init__(self)
        self.name = kwargs['name']
        self.queue = kwargs['queue']
        self.batch_size = kwargs['batch_size']
        self.params = kwargs
        self._skip_()
    def _skip_(self):
        # 建立hbase的链接
        self.connection = happybase.Connection(host='10.30.89.124', port=9090)
        table_name_list = self.connection.tables()
        print('数据库中的表名称', table_name_list)
        h_table_name = 'document_features_test2'
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
        print('hbase中已经存在{}个数据'.format(self.sum_row_hbase))

    def run(self) -> None:
        num_of_into_hbase = 0
        self.client = MongoClient(self.params['url'])
        self.collec = self.client[self.params['db']][self.params['collection']]
        # for one_data in self.collec.find(batch_size=self.batch_size).skip(self.sum_row_hbase):
        for one_data in self.collec.find(batch_size=self.batch_size):
            self.queue.put(one_data)
            num_of_into_hbase += 1
            if num_of_into_hbase % 50 == 0:
                print('向队列中存入了{}个数据。'.format(num_of_into_hbase))
            # if num_of_into_hbase == 10000:
            #     break
        self.client.close()


class Customer(Process):
    def __init__(self, **kwargs):
        Process.__init__(self)
        self.name = kwargs['name']
        self.queue = kwargs['queue']
        self.connection = happybase.Connection(host=kwargs['host'], port=kwargs['port'])
        table_name_list = self.connection.tables()
        print('数据库中的表名称', table_name_list)
        h_table_name = kwargs['h_table_name']
        if h_table_name.encode() not in table_name_list:
            print('{}新建表格。'.format(self.name))
            families = {
                "author": dict(),
                "comment": dict(),
                "document": dict(),
            }
            self.connection.create_table(h_table_name, families)
        self.table = happybase.Table(h_table_name, self.connection)
        self.sum_row_hbase = 0
        for _ in self.table.scan(columns=['author:gender']):
            self.sum_row_hbase += 1
        print('{}，本次执行之前，hbase中{}表中有{}条数据。'.format(self.name, h_table_name, self.sum_row_hbase))
        self.extract_author = ExtractAuthor()
        self.extract_comment = ExtractComment()

    def build_entity(self, one_data, extract_document):
        author = self.extract_author.extract(one_data)
        comment = self.extract_comment.extract(one_data)
        document = extract_document.extract(one_data)
        return author, comment, document

    def merge(self, author, comment, document):
        def merge_one_entity(entity_name, entity):
            return {entity_name + ':' + key: value for key, value in entity.__dict__.items()}

        author_family = merge_one_entity('author', author)
        comment_family = merge_one_entity('comment', comment)
        document_family = merge_one_entity('document', document)
        return {**author_family, **comment_family, **document_family}

    def insert_hbase(self, row_data):
        self.table.put(row_data['author:url_token'] + '_' + str(row_data['document:id']),
                       row_data)

    def run(self) -> None:
        text_vector = TextVector(device_id=int(self.name[-1]))
        hanlptokensner = HanlpTokensNer(
            hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH, devices=int(self.name[-1])))
        extract_document = ExtractDocument(text_vector, hanlptokensner)
        while True:
            one_data = self.queue.get()
            if one_data is None:
                break
            author, comment, document = self.build_entity(one_data, extract_document)
            row_data = self.merge(author, comment, document)
            self.insert_hbase(row_data)
            # print('{}使用了产品{}'.format(self.name, row_data['author:url_token']))
        self.connection.close()


if __name__ == '__main__':
    start_time = time.time()
    queue = Queue(maxsize=100)
    prodece_config = {'name': 'load data', 'queue': queue, 'url': 'mongodb://10.30.89.124:27013/',
                      'db': 'zhihu_new', 'collection': 'articles', 'batch_size': 64}

    p = Producer(**prodece_config)
    num_customers = 4
    customer_config = {'name': '', 'host': '10.30.89.124', 'port': 9090, 'h_table_name': 'document_features_test3',
                       'queue': queue}
    customers = []
    for i in range(num_customers):
        customer_config['name'] = 'Process' + str(i)
        customers.append(Customer(**customer_config))
    p.start()
    for customer in customers:
        customer.start()
    p.join()
    for _ in range(num_customers):
        queue.put(None)
    for customer in customers:
        customer.join()
    print('主进程结束。')
    end_time = time.time()
    print('耗时:{}'.format(end_time - start_time))
    # 一个进程：126.90791893005371
    # 二个进程：112.01390409469604
    # 3个进程：112.0308210849762
    # 6个进程：111.26209473609924
