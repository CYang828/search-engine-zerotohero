# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from ZhiHuScrapy.utils.mongo_utils import MongoUtil
import redis
redis_db = redis.Redis(host='10.30.89.124', port=6379, db=3)
redis_data_dict = "new_article"


class ZhihuscrapyPipeline:
    def process_item(self, item, spider):
        data_dict = dict(item)
        mg_db = MongoUtil('articles')
        # article  能确定唯一的字段
        old_dict = {
            'created': data_dict.get('created'),
            'id': data_dict.get('id'),
        }
        if mg_db.update_one(old_dict, data_dict).matched_count:
            print('update to Mongo, {}'.format(data_dict.get('id')))
        else:
            print('insert to Mongo, {}'.format(data_dict.get('id')))
        return item


class DuplicatesPipeline(object):

    # def __init__(self):
    #     self.article_ids = set()

    def __init__(self):
        redis_db.flushdb()  # 删除全部key，保证key为0，不然多次运行时候hlen不等于0，刚开始这里调试的时候经常出错。
        if redis_db.hlen(redis_data_dict) == 0:  #
            # 从mongo中读取数据
            mg_db = MongoUtil('articles')
            mg_data = mg_db.find_all()
            for i in mg_data:
                article_id = i.get('id')
                redis_db.hset(redis_data_dict, article_id, 0)
            # sql = "SELECT url FROM your_table_name;"  # 从你的MySQL里提数据，我这里取url来去重。
            # df = pd.read_sql(sql, self.conn)  # 读MySQL数据
            # for url in df['url'].get_values():  # 把每一条的值写入key的字段里
            #     redis_db.hset(redis_data_dict, url, 0)  # 把key字段的值都设为0，你要设成什么都可以，因为后面对比的是字段，而不是值。

    def process_item(self, item, spider):
        article_id = item['id']
        # 取item里的id和key里的字段对比，看是否存在，存在就丢掉这个item。不存在返回item给后面的函数处理
        if redis_db.hexists(redis_data_dict, article_id):
            raise DropItem("Duplicate item found -> article_id: %s" % article_id)
            # logging.warning("Duplicate item found: %s" % item)

        else:
            redis_db.hset(redis_data_dict, article_id, 0)

        return item

    # def process_item(self, item, spider):
    #     if item['article_id'] in self.article_ids:
    #         logging.warning("Duplicate item found: %s" % item)
    #
    #     else:
    #         self.article_ids.add(item['article_id'])
    #         return item
