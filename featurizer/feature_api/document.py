# -*- coding:utf-8 -*-
# @Time   :2022/4/20 1:14 下午
# @Author :Li Meng qi
# @FileName:document.py
import happybase



class DocumentFeature:
    def __init__(self, **kwargs):
        self.connect(kwargs)

    def connect(self, params):
        self.connection = happybase.Connection(host=params['host'], port=params['port'])
        self.table = self.connection.table(params['table_name'])

    def get(self, row_key):
        row_key_data = self.table.row(row=row_key)
        row_key_data2 = {}
        for k, v in row_key_data.items():
            row_key_data2[k.decode()] = v.decode()
        return row_key_data2

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    util = DocumentFeature()
    res = util.get(row_key='zhang-jue-fei_25249694')
    print(res)