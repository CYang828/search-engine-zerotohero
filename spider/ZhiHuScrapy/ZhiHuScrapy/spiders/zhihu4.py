import json
import logging
import os
import time

import scrapy

from ZhiHuScrapy.items import ZhihuscrapyItem, ZhihuArticalItem
from ZhiHuScrapy.utils.mongo_utils import MongoUtil
from ZhiHuScrapy.settings import BASE_DIR


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu4'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://zhuanlan.zhihu.com/api/recommendations/columns?limit=8&offset=8&seed=7']
    with open(os.path.join(BASE_DIR, 'libs/cookie.txt')) as f:
        cookie = f.read()
    headers = {
        "referer": "https://www.zhihu.com/search?type=content&q=python",
        "cookie": cookie,
    }

    # cookies_str = """d_c0="AIDmM_fFPg-PTrszhny3HjZNq2sT9ooxYZo=|1554690682"; __utmv=51854390.100-1|2=registration_date=20190522=1^3=entry_date=20190408=1; _ga=GA1.2.717760570.1558511386; __snaker__id=l8ad3URU6vNoK3Da; _9755xjdesxxd_=32; YD00517437729195%3AWM_TID=d3c0%2FNGzdD9ARAVAUVcvlQ%2BIfUW%2FKjXI; _zap=44523947-3f50-47ae-bba3-1986ace216d8; gdxidpyhxdE=c%5CyNXzB2u2OIuK0%2Bj3jENquDzh5kHuD19Mqbl29ccHQcERmHTQOnMDlnCyCwcxBLjkf%2F4M2sdBToWRnlu%5C4GDNoNs%2BJlcCn%5CmCXIJ0Weya6Z6Jkw5ZIHOPxsm8g9JBEzQLPYUI0pJBAw9TVaiBSMb4ZtHTorN%5CZTVQNKEcNdpwQUuy%5CR%3A1627553347396; YD00517437729195%3AWM_NI=QX9%2Fk9iTohmqt9Ev4SfB1jIzSrCvpGs%2FZeEBz%2Btwm3dzlBILEfmhw4JfZFEy9LG%2FKQlmT85960PiqijzwzXOGXW5UWLcvxfFK3kwgXMbQ%2BKe8n2STeC9cAaItex4LZomQnQ%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6eea4d23bb5b4aa94ae7bf4b88ba3c54b969a9b84f5678db0998be179f6ebfc9bf22af0fea7c3b92a9388f7d0ea33ab8ca189f07bb8e78b97b759a69eff8bcc7291ae8d97f34db1f19686c84abaf5bc98f039a8a6a4a3cc4887baa389f6408aba96a7c873fb9489d0ca5bb0b39cd9b833f6f0a08af463aaa6b99bdb45858899d6d85d90bdba99e54e89eda598e6548fbe9fccca6ffcb2feb4d76f81e7ada2e443b8bbb8d5cf52adb39f8fd437e2a3; l_n_c=1; n_c=1; z_c0=Mi4xNHlQWUR3QUFBQUFBZ09Zejk4VS1EeGNBQUFCaEFsVk42Y2p2WVFEdHNPVTdKY3J6ZmZuLWl4MFpuUWxKamp5N293|1627552489|268a6f05e436a067238e29b67aaf4b9a3cd4c9db; _xsrf=6918ecfc-d48e-4277-9b05-4f4bb338778c; SESSIONID=oPm5jWgUluTCPetquHRZWtTW2rSeeqTdWm0kCeUVAeO; JOID=UV8VBU0NSjkhqV58AgirIehBpewQZh1SFMYNHFFkO2pk-T4MdBubt0WoXX0EkoVVzHr6fmlXTcp877JbnzayRXY=; osd=U18RAU8PSj0lq1x8BgypI-hFoe4SZhlWFsQNGFVmOWpg_TwOdB-ftUeoWXkGkIVRyHj4fm1TT8h867ZZnTa2QXQ=; q_c1=aeaab8b62f3f435597a5d8ebc04238f8|1636357302000|1554690684000; __utma=51854390.717760570.1558511386.1582534383.1636357304.3; __utmc=51854390; __utmz=51854390.1636357304.3.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1636431752,1636459784,1636511754,1636543664; tst=r; NOT_UNREGISTER_WAITING=1; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1636612666; KLBRSID=ca494ee5d16b14b649673c122ff27291|1636613257|1636612359"""

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.cookies = self.transform(self.cookies_str)

    @staticmethod
    def transform(cookies):
        cookie_dict = {}
        cookies = cookies.replace(' ', '')
        list = cookies.split(';')
        for i in list:
            keys = i.split('=')[0]
            values = i.split('=')[1]
            cookie_dict[keys] = values
        return cookie_dict

    def start_requests(self):
        start_urls = [f'https://zhuanlan.zhihu.com/api/recommendations/columns?limit={8}&offset={i * 8}&seed=7'
                      for i in range(80000000, 100000000)]

        # start_urls = ['https://zhuanlan.zhihu.com/api/recommendations/columns?limit=8&offset=8&seed=7']
        for url in start_urls:
            logging.warning(f'当前爬虫专栏URL为{url}')
            time.sleep(0.5)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_zhuanlan, meta={'url': url})

    def parse_zhuanlan(self, response):
        zhuanlan_data = response.json()
        url = response.meta.get('url')
        zhuanlan_lists = zhuanlan_data.get('data')

        for i in zhuanlan_lists:
            if not i:
                logging.warning(f'{url}没有解析出相应的数据')
                continue
            item = ZhihuscrapyItem()
            item['updated'] = i.get('updated')
            item['description'] = i.get('description')
            item['column_type'] = i.get('column_type')
            item['title'] = i.get('title')
            item['url'] = i.get('url')
            item['comment_permission'] = i.get('comment_permission')
            item['created'] = i.get('created')
            item['accept_submission'] = i.get('accept_submission')
            item['intro'] = i.get('intro')
            item['image_url'] = i.get('image_url')
            item['type'] = i.get('type')
            item['followers'] = i.get('followers')
            item['url_token'] = i.get('url_token')
            item['id'] = i.get('id')
            item['articles_count'] = i.get('articles_count')
            time.sleep(0.1)
            # print(item['url'])
            # c_url = f"https://www.zhihu.com/api/v4/columns/{item['url_token']}/items"
            pages = item['articles_count'] // 20 + 1
            # params = {
            #     'limit': 10,
            #     'offset': 10
            # }
            # mg_db = MongoUtil('zhuanlan')
            # # article  能确定唯一的字段
            # old_dict = {
            #     'created': i.get('created'),
            #     'id': i.get('id'),
            # }
            # if mg_db.update_one(old_dict, i).matched_count:
            #     logging.warning('专栏已爬过，update to Mongo-zhuanlan, {}'.format(i.get('id')))
            #     continue
            # else:
            #     logging.warning('专栏入库，insert to Mongo-zhuanlan, {}'.format(i.get('id')))
            # cur_url = f"https://www.zhihu.com/api/v4/columns/{item['url_token']}/items?limit={10}&offset={10}"
            # yield scrapy.Request(url=cur_url,
            #                      headers=self.headers,
            #                      # body=json.dumps(params),
            #                      callback=self.parse_article)
            for j in range(0, pages):
                cur_url = f"https://www.zhihu.com/api/v4/columns/{item['url_token']}/items?limit={20}&offset={j * 20}"
                yield scrapy.Request(url=cur_url,
                                     headers=self.headers,
                                     # body=json.dumps(params),
                                     callback=self.parse_article,
                                     meta=item)

    def parse_article(self, response):
        articles_data = response.json()
        zhuanlan_item = response.meta
        mg_db = MongoUtil('zhuanlan')
        old_dict = {
            'created': zhuanlan_item['created'],
            'id': zhuanlan_item['id'],
        }
        if mg_db.update_one(old_dict, dict(zhuanlan_item)).matched_count:
            logging.warning('专栏已爬过，update to Mongo-zhuanlan, {}'.format(zhuanlan_item['id']))
        else:
            logging.warning('专栏入库，insert to Mongo-zhuanlan, {}'.format(zhuanlan_item['id']))

        for article in articles_data.get('data'):
            if not article:
                continue
            article_item = ZhihuArticalItem()
            article_item['updated'] = article.get('updated')
            article_item['is_labeled'] = article.get('is_labeled')
            article_item['copyright_permission'] = article.get('copyright_permission')
            article_item['settings'] = article.get('settings')
            article_item['excerpt'] = article.get('excerpt')
            article_item['admin_closed_comment'] = article.get('admin_closed_comment')
            article_item['voting'] = article.get('voting')
            article_item['article_type'] = article.get('article_type')
            article_item['reason'] = article.get('reason')
            article_item['excerpt_title'] = article.get('excerpt_title')
            article_id = article.get('id')
            article_item['id'] = article_id
            article_item['voteup_count'] = article.get('voteup_count')
            article_item['title_image'] = article.get('title_image')
            article_item['has_column'] = article.get('has_column')
            article_item['url'] = article.get('url')
            article_item['comment_permission'] = article.get('comment_permission')
            article_item['author'] = article.get('author')
            comment_count = article.get('comment_count')
            assert isinstance(comment_count, int), '评论数为整数！'
            article_item['comment_count'] = comment_count
            article_item['created'] = article.get('created')
            article_item['content'] = article.get('content')
            article_item['state'] = article.get('state')
            article_item['image_url'] = article.get('image_url')
            article_item['title'] = article.get('title')
            article_item['can_comment'] = article.get('can_comment')
            article_item['type'] = article.get('type')
            article_item['suggest_edit'] = article.get('suggest_edit')
            pages = comment_count // 20 + 1
            if not pages:
                yield article_item
            # comment_url = f'https://www.zhihu.com/api/v4/articles/{article_id}/root_comments?order=normal&limit=20&offset=0&status=open'
            for j in range(0, pages):
                time.sleep(0.1)
                comment_url = f'https://www.zhihu.com/api/v4/articles/{article_id}/root_comments?order=normal&limit=20&offset={j * 20}&status=open'
                yield scrapy.Request(url=comment_url,
                                     headers=self.headers,
                                     callback=self.parse_article_comment,
                                     meta=article_item)
            # yield article_item

    def parse_article_comment(self, response):
        comment_data = response.json()
        # print(comment_data)
        # logging.warning(comment_data.get('data'))
        article_item = response.meta
        article_item['comments'] = comment_data.get('data')
        yield article_item
