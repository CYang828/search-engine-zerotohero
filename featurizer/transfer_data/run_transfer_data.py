# -*- coding:utf-8 -*-
# @Time   :2022/4/6 4:47 下午
# @Author :Li Meng qi
# @FileName:run_transfer_data.py
import happybase
from pyhive import hive
import json
from multiprocessing import Process, Queue
import time


class Producer(Process):
    def __init__(self, **kwargs):
        Process.__init__(self)
        self.queue = kwargs['queue']
        self.batch_size = kwargs['batch_size']
        self.connect_hbase(kwargs)
        self.kwargs = kwargs

    def connect_hbase(self, params):
        self.hbase_connection = happybase.Connection(host="10.30.89.124", port=9090, timeout=None)
        self.table = self.hbase_connection.table(params['table_name'])

    def run(self) -> None:
        row_start = None
        i = 0
        flag = True
        skip_first_one = False
        while flag:
            try:
                rows = self.table.scan(batch_size=self.batch_size, row_start=row_start)
                for row in rows:
                    if skip_first_one:
                        skip_first_one = False
                        continue
                    self.queue.put(row)
                    row_key = row[0]
                    i += 1
                    if i % 100 == 0:
                        print(i)
                print(i)
                flag = False
            except Exception as e:
                flag = True
                print(e.__str__())
                row_start = row_key
                self.connect_hbase(self.kwargs)
                skip_first_one = True
        self.hbase_connection.close()


class Customer(Process):
    def __init__(self, **kwargs):
        Process.__init__(self)
        self.name = kwargs['name']
        self.queue = kwargs['queue']
        self.connect_hbase(kwargs)
        self.connect_hive(kwargs)
        self.table_name = kwargs['table_name']

    def byte2cahr(self, bytedict):
        return {k.decode(): v.decode() for k, v in bytedict.items()}

    def connect_hbase(self, params):
        self.hbase_connection = happybase.Connection(host="10.30.89.124", port=9090, timeout=None)
        if params['table_name'] == 'user_features':
            row = 'userid_000000'
        elif params['table_name'] == 'document_features_test3':
            row = 'zhang-jue-fei_25249694'
        else:
            row = ''
        self.table = self.hbase_connection.table(params['table_name'])
        self.field_name = ['_'.join(k.decode().split(':')) for k, v in self.table.row(row).items()]
        print(self.field_name)

    def connect_hive(self, params):
        self.hive_connection = hive.Connection(host='10.30.89.124', port=10000, database='search_engine_features')
        self.curs = self.hive_connection.cursor()
        create_table_sql = """create table if not exists {}
                            (row_key String,
                             {}
                             )   
                               """.format(params['table_name'],
                                          ',\n'.join([name + ' ' + 'varchar(65535)' for name in self.field_name]))
        # print(create_table_sql)
        self.curs.execute(create_table_sql)
    def run(self) -> None:
        while True:
            one_data = self.queue.get()
            if one_data is None:
                break
            file_name_values = [one_data[0].decode()]
            file_name = ['row_key']
            temp = self.byte2cahr(one_data[1]).items()
            for k, v in temp:
                if not v:
                    v = ''
                file_name_values.append(v)
                file_name.append(k.replace(':', '_'))
            file_name = ','.join(file_name)
            # print(file_name_values[21])
            # print(self.byte2cahr(one_data[1])['document:title'])
            sql = """insert into {} ({}) values {}""".format(self.table_name, file_name, tuple(file_name_values))
            # print(self.name, '---', sql.split('values')[0])
            self.curs.execute(sql)
        self.close()

    def close(self):
        self.hbase_connection.close()
        self.hive_connection.close()


if __name__ == '__main__':
    start_time = time.time()
    queue = Queue(maxsize=256)
    config = {'table_name': 'document_features_test3', 'queue': queue, 'batch_size': 64, 'host': '10.30.89.124'}

    p = Producer(**config)
    num_customers = 6
    customers = []
    for i in range(num_customers):
        config['name'] = 'Process' + str(i)
        customers.append(Customer(**config))
    p.start()
    for customer in customers:
        customer.start()
    p.join()
    for _ in range(num_customers):
        queue.put(None)
    for customer in customers:
        customer.join()
    print('主进程结束。')
    # end_time = time.time()
    # print('耗时:{}'.format(end_time - start_time))
