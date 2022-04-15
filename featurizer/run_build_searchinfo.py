# -*- coding:utf-8 -*-
# @Time   :2022/3/30 6:47 下午
# @Author :Li Meng qi
# @FileName:run_build_searchinfo.py
import happybase
from extract_entity.extract_searchinfo import ExtractSearchInfo
import pandas as pd
from multiprocessing import Process, Queue


class Processer:
    def __init__(self, **kwargs):
        self.connect(kwargs)
        # 处理
        self.extract_entity = ExtractSearchInfo()
        self.data_path = kwargs["data_path"]
        self.row_key = 0
        self.batch_size = 256
        self.num_customer = 6

    def connect(self, kwargs):
        # 建立hbase的链接
        self.connection = happybase.Connection(host=kwargs["host"], port=kwargs["port"])
        table_name_list = self.connection.tables()
        print("数据库中的表名称", table_name_list)
        h_table_name = kwargs["h_table_name"]
        if h_table_name.encode() not in table_name_list:
            families = {
                "searchinfo": dict(),
            }
            self.connection.create_table(h_table_name, families)
        self.table = happybase.Table(h_table_name, self.connection)
        self.sum_row_hbase = 0
        for _ in self.table.scan(columns=["searchinfo:click"]):
            self.sum_row_hbase += 1
        print("本次执行之前，hbase中{}表中有{}条数据。".format(h_table_name, self.sum_row_hbase))

    def load_from_csv(self):
        df = pd.read_csv(self.data_path, iterator=True, chunksize=self.batch_size)
        return df

    def build_entity(self, one_data):
        user = self.extract_entity.extract(one_data)
        return user

    def merge(self, entity):
        def merge_one_entity(entity_name, entity):
            return {
                entity_name + ":" + key: value for key, value in entity.__dict__.items()
            }

        entity_family = merge_one_entity("searchinfo", entity)
        return {**entity_family}

    def insert_hbase(self, row_key, row_data):
        self.table.put(str(row_key), row_data)

    def _process_one_data(self, q, name):
        while True:
            one_data = q.get()
            if one_data is None:
                break
            entity = self.build_entity(one_data)
            row_data = self.merge(entity)
            row_key = one_data[0]
            self.insert_hbase(row_key, row_data)
            # print(name + ': ' + str(row_data))

    def _reconstruct_data(self, batch_data):
        datas = []
        batch_data = batch_data.to_dict()
        for key, value in batch_data.items():
            datas.append([v for k, v in value.items()])
        for info in zip(*datas):
            yield info

    def producer(self, q):
        self.num_of_into_hbase = 0
        for batch_data in self.load_from_csv():
            for one_data in self._reconstruct_data(batch_data):
                q.put([self.num_of_into_hbase] + list(one_data))
                self.num_of_into_hbase += 1
                if self.num_of_into_hbase % 1000 == 0:
                    print("向队列中存入了{}个数据。".format(self.num_of_into_hbase))

    def run(self):
        q = Queue(maxsize=10000)
        # 生产者：往q中追加数据
        p1 = Process(target=self.producer, args=(q,))
        # 消费者往数据库中存数据
        customers = [
            Process(target=self._process_one_data, args=(q, "c" + str(i)))
            for i in range(self.num_customer)
        ]
        p1.start()
        for customer in customers:
            customer.start()
        p1.join()
        for _ in range(self.num_customer):
            q.put(None)
        for customer in customers:
            customer.join()
        print("主")
        print("本次从csv中一共转移{}条数据到hbase".format(self.num_of_into_hbase))
        self.close()

    def close(self):
        self.connection.close()


if __name__ == "__main__":
    process = Processer(
        host="10.30.89.124",
        port=9090,
        data_path="data/search_information.csv",
        h_table_name="searchinfo_features",
    )
    process.run()
