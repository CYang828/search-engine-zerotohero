# @Time    : 2021-11-29 18:47
# @Author  : 老赵
# @File    : crawlall.py
import logging

from scrapy.commands import ScrapyCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class Command(ScrapyCommand):
    requires_project = True

    def syntax(self):
        return "[options]"

    def short_desc(self):
        return "Runs all of the spiders"

    def run(self, args, opts):
        spider_list = self.crawler_process.spiders.list()
        logging.warning(spider_list)
        self.run_process_spiders(spider_list)
        # for name in spider_list:
        #     self.crawler_process.crawl(name, **opts.__dict__)
        # self.crawler_process.start()

    @staticmethod
    def run_process_spiders(spider_list=None):
        process = CrawlerProcess(get_project_settings())
        for spider in spider_list:
            process.crawl(spider)
        process.start()
