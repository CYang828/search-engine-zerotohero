import json
import time

import scrapy

from ZhiHuScrapy.items import ZhihuscrapyItem, ZhihuArticalItem
from ZhiHuScrapy.utils.mongo_utils import MongoUtil


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://zhuanlan.zhihu.com/api/recommendations/columns?limit=8&offset=8&seed=7']
    headers = {
        "referer": "https://www.zhihu.com/search?type=content&q=python",
        "cookie": 'd_c0="AIDmM_fFPg-PTrszhny3HjZNq2sT9ooxYZo=|1554690682"; __utmv=51854390.100-1|2=registration_date=20190522=1^3=entry_date=20190408=1; _ga=GA1.2.717760570.1558511386; _zap=44523947-3f50-47ae-bba3-1986ace216d8; l_n_c=1; n_c=1; _xsrf=6918ecfc-d48e-4277-9b05-4f4bb338778c; q_c1=aeaab8b62f3f435597a5d8ebc04238f8|1636357302000|1554690684000; __utma=51854390.717760570.1558511386.1582534383.1636357304.3; __utmc=51854390; __utmz=51854390.1636357304.3.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); tst=r; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1636613746,1636613788,1636613797,1636625578; SESSIONID=xbGLOWgWurYiHxXCyiB42ctCMcSYUL2CnzSyBkQnYgQ; JOID=UV0RB015A0iCNX8YeX7gVEvZhopvEFIltVoufiwQcB3BZx9qCSHyxuQ2eBl71QYowg20lvZ_tkZyQImX72XZgpI=; osd=VFAUAEp8Dk2FMnoVfHnnUUbcgY1qHVcisl8jeysXdRDEYBhvBCT1weE7fR580AstxQqxm_N4sUN_RY6Q6mjchZU=; captcha_session_v2="2|1:0|10:1636687569|18:captcha_session_v2|88:cmNVdWhkNGU2aFNTeGZBRWJGckUzdk5aMkRBYkpWaGxKN2R0bSs4REFHQkY2eG01Z3FjVlNETzVaTEg0a1NxYg==|71f623f1ef178dfc871c9ad25184eac697f929b6b17534fb8cc35d78e84c0148"; __snaker__id=Zj4klu6YHSp2qFjh; gdxidpyhxdE=bqxtlK9CB2Iu0%2FG%2Blxw%2BI%2B%5Cq5XCqM1ifRppgr9DSurZ9s%2Bcz3zK5bP3SelOo41HyVnmODhuLw%2Fs%2FdWUo%5C%2BYnl7m1JgX19u%2FHSUlYcyyfCRj08gNNLkah5UDyt%2BAJkcjcA0lHGV1orc8yS8%2FGMEwzT2dAQ2RdQi2I7%5CZ6SYKNnxUHtdGr%3A1636688470673; _9755xjdesxxd_=32; YD00517437729195%3AWM_NI=f%2FkK%2FABCmOn3JbsSuh9R%2BGh814jeylysVpyAU38hTtoU%2B4nTYMkA4GgqCaMJTyfU49XlvTmq6cKjo2ne6ZdERebcg%2FrEBdW53%2FCK0IQ5srptDDefi4VWHuVIWwV0eHd4ZmQ%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6eea7f14897bd8184b74189868aa7c45a928e8abbae7cb59783b9e43cf7a88984b62af0fea7c3b92aa6f1a5acae4b829da3b0ed398abebdb4f864fb8ee5a8eb34f3eca686fc68bbad9a91fc4b97edf889d780ad8be5d5ed609b93a5a2b74da5af8d82d04298a7aab6b7339cb4bab5f07bf6bd858bee3aaebbfabbe74f92bbae84e625b29b8e85d63ff1f18dacb34393ebbd93f380889cab87ec4096898896d54395a99ad1e844a8ec968ed437e2a3; YD00517437729195%3AWM_TID=Yl0%2BpoY8FRVEQQBEVVcvtwcYTPx51Dd6; captcha_ticket_v2="2|1:0|10:1636687605|17:captcha_ticket_v2|704:eyJ2YWxpZGF0ZSI6IkNOMzFfU09ZZVhudXlMZU9HR1guSXp4cHhGUTQuQUc0WTZ5RllYT1h1Z2twX2VIV2FYOUZnMW11WW5mMXdTcTFLNzcxMWtMVUdzNHdNQnR2dWhjVTYwNEVnbVgwRHpEcVl5RVR4dkN5dWRPZ1Y1UXlsVTdfLjRucVhQUmxKYk9lY0NlamJCbVFjWTFLcGZhQmpoMExuMi1Gc21YTk9wR3Y4a0pBLVpfX1hMZm1UNW1FRDR0NjJYby5KVE5tWHMwWXBlVXppb2dDNGRsWnJ4UzZXX1YuNmRocnRrQ2Q1U2YxZjhvRFdLR29kTkNKMDRWTjc4RC0tMVVzRWtWMmRlR2ZZeURBYnBaa3RZTnRjSi50cDRCNVFFRGZkQ1dGcVNxRlRpYVAtdmxYeFVKaHlyTVp6LVBwdlM1V2FHR2tNQ0pfZkVELS1FZkEyOXF1YkR5cFZoTkdKS2IyQ0E1VzZQLWpoWnlueHdWOXFObFNhQnN4ZGxoVHNUSjRLRTVtcVYyei55cFZHQjBCRnlNUEVPa0ROOUU3S1JRNU5lV1RCRFctVmc4V3NtWVZYZWJvNTVtb2Q5aDhTcDZhLm5UZHlDRHhJak1xSzZiT0w0RUIyYXg2VzVPWUVSY2hYdkl6dTZFR2x1VjQ5Q3FMQzB4OGk3WXRsLVAtSTIyV2U5YjF2b2VyMyJ9|c5f588c91f433bfb459c24fdce0283fc8f9399f3f8e9e99e4dc5e422b3ac720d"; z_c0="2|1:0|10:1636687622|4:z_c0|92:Mi4xbGlmRE13QUFBQUFBZ09Zejk4VS1EeVlBQUFCZ0FsVk5CaTE3WWdDZUFMbUdYVU9pTXBSeXpuVlZ1dWkxakpBYjl3|174e4b0012a39c6f83b4c83040836e9f51718703dbbf2218df02542d0987415b"; unlock_ticket="AXBe-Y2DAxQmAAAAYAJVTQ7mjWE82Plq1cto8aK96oF_MPq-iwNtig=="; KLBRSID=3d7feb8a094c905a519e532f6843365f|1636687622|1636686599; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1636687623; NOT_UNREGISTER_WAITING=1',
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
        start_urls = [f'https://zhuanlan.zhihu.com/api/recommendations/columns?limit={8}&offset={i*8}&seed=7'
                      for i in range(1, 100000000)]

        # start_urls = ['https://zhuanlan.zhihu.com/api/recommendations/columns?limit=8&offset=8&seed=7']
        for url in start_urls:
            time.sleep(3)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse_zhuanlan)

    def parse_zhuanlan(self, response):
        zhuanlan_data = response.json()
        zhuanlan_lists = zhuanlan_data.get('data')

        for i in zhuanlan_lists:
            if not i:
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
            time.sleep(1)
            # print(item['url'])
            # c_url = f"https://www.zhihu.com/api/v4/columns/{item['url_token']}/items"
            pages = item['articles_count'] // 10 + 1
            params = {
                'limit': 10,
                'offset': 10
            }
            mg_db = MongoUtil('zhuanlan')
            # article  能确定唯一的字段
            old_dict = {
                'created': i.get('created'),
                'id': i.get('id'),
            }
            if mg_db.update_one(old_dict, i).matched_count:
                print('update to Mongo-zhuanlan, {}'.format(i.get('id')))
                continue
            else:
                print('insert to Mongo-zhuanlan, {}'.format(i.get('id')))
            # cur_url = f"https://www.zhihu.com/api/v4/columns/{item['url_token']}/items?limit={10}&offset={10}"
            # yield scrapy.Request(url=cur_url,
            #                      headers=self.headers,
            #                      body=json.dumps(params),
            #                      callback=self.parse_article)
            for j in range(1, pages+1):
                cur_url = f"https://www.zhihu.com/api/v4/columns/{item['url_token']}/items?limit={10}&offset={j*10}"
                yield scrapy.Request(url=cur_url,
                                     headers=self.headers,
                                     body=json.dumps(params),
                                     callback=self.parse_article,
                                     meta=item)

    def parse_article(self, response):
        articles_data = response.json()
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
            article_item['id'] = article.get('id')
            article_item['voteup_count'] = article.get('voteup_count')
            article_item['title_image'] = article.get('title_image')
            article_item['has_column'] = article.get('has_column')
            article_item['url'] = article.get('url')
            article_item['comment_permission'] = article.get('comment_permission')
            article_item['author'] = article.get('author')
            article_item['comment_count'] = article.get('comment_count')
            article_item['created'] = article.get('created')
            article_item['content'] = article.get('content')
            article_item['state'] = article.get('state')
            article_item['image_url'] = article.get('image_url')
            article_item['title'] = article.get('title')
            article_item['can_comment'] = article.get('can_comment')
            article_item['type'] = article.get('type')
            article_item['suggest_edit'] = article.get('suggest_edit')
            yield article_item
