# @Time    : 2021-11-11 17:32
# @Author  : 老赵
# @File    : mongo_utils.py

import pymongo


class MongoUtil:

    def __init__(self, myset):
        client = pymongo.MongoClient(host='10.30.89.124', port=27011)
        # client = pymongo.MongoClient('mongodb://{}:{}@{}:{}/'.format(
        #     "bigdata", "bigdata123", "10.30.89.124", "27011"))
        self.collection = client.zhihu_data[f'{myset}']

    def mongo_insert(self, data_dict):
        ret = self.collection.insert_one(data_dict)
        return ret

    def mongo_insert_many(self, data_list):
        ret = self.collection.insert_many(data_list)
        return ret

    def update_one(self, old_dict, new_dict):
        return self.collection.update_one(old_dict, {'$set': new_dict}, upsert=True)

    def delete_one(self, data_dict):
        self.collection.delete_one(data_dict)

    def find_one(self, data_dict):
        t = self.collection.find_one(data_dict)
        return t

    def find_all(self):
        t = self.collection.find()
        return (i for i in t)


if __name__ == '__main__':
    mg_db = MongoUtil('articles')
    # # 插入数据
    # student = {'id': '20190101', 'name': 'Tom3', 'age': 20, 'gender': 'female'}
    # ret = mg_db.mongo_insert(student)
    # print('insert_id:', ret.inserted_id)
    # # mongo_data = mg_db.find_one({'imdb_id': '0113497'})
    # # print(mongo_data, type(mongo_data))
    mongo_data = mg_db.find_all()
    # print(mg_db.collection.find())
    for i in mongo_data:
        print(i)
