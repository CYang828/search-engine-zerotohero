# -*- coding:utf-8 -*-
# @Time   :2022/4/11 2:28 下午
# @Author :Li Meng qi
# @FileName:run_load_hbase_to_csv.py
import happybase
import pandas as pd
import json
import numpy as np


class LoadHbase:
    def __init__(self, **kwargs):
        self.batch_size = kwargs['batch_size']
        self.kwargs = kwargs
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.connect_hbase(kwargs)
        self.file_path = 'document_features.txt'
        self.open_file()
        self.reserved_fields = kwargs['rf']

    def open_file(self):
        self.f_write = open(self.file_path, 'a', encoding='utf-8')

    def connect_hbase(self, params):
        self.hbase_connection = happybase.Connection(host=self.host, port=self.port)
        self.table = self.hbase_connection.table(params['table_name'])

    def close(self):
        self.f_write.close()
        self.hbase_connection.close()

    def byte2cahr(self, bytedict):
        return {k.decode(): v.decode() for k, v in bytedict.items()}

    def list2char(self, item):
        return np.array2string(np.array(item)).replace('\n', '').replace(',', '，')

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
                    file_name = ['row_key']
                    file_name_values = [row[0].decode()]
                    row_key = row[0].decode()
                    temp = self.byte2cahr(row[1]).items()
                    for k, v in temp:
                        if k not in self.reserved_fields:
                            continue
                        if k == 'comment:avatar_url_list':
                            v = json.loads(v)["avatar_url_list"]
                            v = self.list2char(v)
                        elif k == 'comment:content_list':
                            v = json.loads(v)['content_list']
                            v = self.list2char(v)
                        elif k == 'comment:created_time_list':
                            v = json.loads(v)['created_time_list']
                            v = self.list2char(v)
                        elif k == 'comment:name_list':
                            v = json.loads(v)['name_list']
                            v = self.list2char(v)
                        elif k == 'comment:url_token_list':
                            v = json.loads(v)['url_token_list']
                            v = self.list2char(v)
                        elif k == 'comment:vote_count_list':
                            v = json.loads(v)['vote_count_list']
                            v = self.list2char(v)
                        elif k == 'document:clean_content_vector':
                            v = json.loads(v)['clean_content_vector']
                            v = self.list2char(v)
                        elif k == 'document:title_vector':
                            v = json.loads(v)['title_vector']
                            v = self.list2char(v)
                        elif k == 'document:tokens':
                            v = json.loads(v)['tok_fine']
                            v = self.list2char(v)
                        elif k == 'document:top5words':
                            v = json.loads(v)['top5word']
                            v = self.list2char(v)
                        elif k == 'document:excerpt_vector':
                            v = json.loads(v)['excerpt_vector']
                            v = self.list2char(v)
                        else:
                            v = v.replace(',', '，').replace('\n', '')
                        file_name_values.append(v)
                        file_name.append(k)
                    self.f_write.write(','.join(file_name_values) + '\n')
                    row_key = row[0]
                    i += 1
                    if i % 100 == 0:
                        print('已经移动', i)
                print(i)
                flag = False
            except Exception as e:
                flag = True
                print(e)
                row_start = row_key
                self.connect_hbase(self.kwargs)
                skip_first_one = True
        self.hbase_connection.close()
        self.close()


if __name__ == '__main__':
    field_name = ['author:avatar_url',
                  'author:description',
                  'author:gender',
                  'author:headline',
                  'author:id',
                  'author:is_advertiser',
                  'author:name',
                  'author:url',
                  'author:url_token',
                  'author:user_type',
                  'comment:avatar_url_list',
                  'comment:comment_count',
                  'comment:content_list',
                  'comment:created_time_list',
                  'comment:name_list',
                  'comment:url_token_list',
                  'comment:vote_count_list',
                  'comment:voteup_count',
                  'document:clean_content',
                  'document:clean_content_vector',
                  'document:created',
                  'document:entity',
                  'document:excerpt',
                  'document:excerpt_vector',
                  'document:has_column',
                  'document:id',
                  'document:image_url',
                  'document:title',
                  'document:title_vector',
                  'document:tokens',
                  'document:top5words',
                  'document:type',
                  'document:updated', ]
    config = {'table_name': 'document_features_test3', 'host': '10.30.89.124', 'port': 9090, 'batch_size': 64,
              'field_name': field_name, 'rf': field_name}
    loadhbase = LoadHbase(**config)
    loadhbase.run()
