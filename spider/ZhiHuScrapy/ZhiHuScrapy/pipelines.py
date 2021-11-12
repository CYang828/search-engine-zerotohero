# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from ZhiHuScrapy.utils.mongo_utils import MongoUtil


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
