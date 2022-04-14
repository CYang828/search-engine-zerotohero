# -*- coding:utf-8 -*-
# @Time   :2022/2/24 11:21 上午
# @Author :Li Meng qi
# @FileName:run_build_user.py
from pymongo import MongoClient
import happybase
from extract_entity.extract_user import ExtractUser
import pandas as pd


class Processer:

    def __init__(self, **kwargs):
        self.connect(kwargs)
        # 处理
        self.extract_author = ExtractUser()
        self.data_path = kwargs['data_path']

    def connect(self, kwargs):
        # 建立hbase的链接
        self.connection = happybase.Connection(host=kwargs['host'], port=kwargs['port'])
        table_name_list = self.connection.tables()
        print('数据库中的表名称', table_name_list)
        h_table_name = kwargs['h_table_name']
        if h_table_name.encode() not in table_name_list:
            families = {
                "user": dict(),
            }
            self.connection.create_table(h_table_name, families)  # 创建表格
        self.table = happybase.Table(h_table_name, self.connection)  # 获取表格对象
        self.sum_row_hbase = 0
        # userid	gender	age	city	job	education
        for _ in self.table.scan(columns=['user:gender']):
            self.sum_row_hbase += 1
        print('本次执行之前，hbase中{}表中有{}条数据。'.format(h_table_name, self.sum_row_hbase))

    def load_from_csv(self):
        df = pd.read_csv(self.data_path, iterator=True, chunksize=8, skiprows=self.sum_row_hbase)
        return df

    def build_entity(self, one_data):
        user = self.extract_author.extract(one_data)
        return user

    def merge(self, user):
        def merge_one_entity(entity_name, entity):
            return {entity_name + ':' + key: value for key, value in entity.__dict__.items()}
        user_family = merge_one_entity('user', user)
        return {**user_family}

    def insert_hbase(self, row_data):
        # print(row_data['user:userid'])
        self.table.put(row_data['user:userid'],
                       row_data)

    def _process_one_data(self, one_data):
        user = self.build_entity(one_data)
        row_data = self.merge(user)
        self.insert_hbase(row_data)
    def _reconstruct_data(self, batch_data):
        datas = []
        batch_data = batch_data.to_dict()
        for key, value in batch_data.items():
            datas.append([v for k, v in value.items()])
        for user_info in zip(*datas):
            yield user_info

    def run(self):
        num_of_into_hbase = 0
        for batch_data in self.load_from_csv():
            for one_data in self._reconstruct_data(batch_data):
                num_of_into_hbase += 1
                self._process_one_data(one_data)
                if num_of_into_hbase % 100 == 0:
                    print('已经处理{}条数据。'.format(num_of_into_hbase))
        print('本次从csv中一共转移{}条数据到hbase'.format(num_of_into_hbase))
        self.close()

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    process = Processer(host='10.30.89.124', port=9090, data_path='/Users/lmq/Downloads/user_data.csv',
                        h_table_name='user_features')
    process.run()
