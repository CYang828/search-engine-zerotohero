# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    updated = scrapy.Field()  # 更新时间
    description = scrapy.Field()  # 描述
    column_type = scrapy.Field()  #
    title = scrapy.Field()  # 标题
    url = scrapy.Field()  # 专栏url
    comment_permission = scrapy.Field()  # comment_permission
    created = scrapy.Field()  # 创建时间
    accept_submission = scrapy.Field()  # accept_submission
    intro = scrapy.Field()  # intro
    image_url = scrapy.Field()  # 图片url
    type = scrapy.Field()  # type
    followers = scrapy.Field()  # 关注人数
    url_token = scrapy.Field()  # url_token
    id = scrapy.Field()  # id
    articles_count = scrapy.Field()  # 文章数


class ZhihuArticalItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    updated = scrapy.Field()  # 更新时间
    is_labeled = scrapy.Field()  #
    copyright_permission = scrapy.Field()  #
    settings = scrapy.Field()  #
    excerpt = scrapy.Field()  #
    admin_closed_comment = scrapy.Field()  #
    voting = scrapy.Field()  #
    article_type = scrapy.Field()  #
    reason = scrapy.Field()  #
    excerpt_title = scrapy.Field()  #
    id = scrapy.Field()  #
    voteup_count = scrapy.Field()  #
    title_image = scrapy.Field()  #
    has_column = scrapy.Field()  #
    url = scrapy.Field()  #
    comment_permission = scrapy.Field()  #
    author = scrapy.Field()  #
    comment_count = scrapy.Field()  #
    comments = scrapy.Field()  #
    created = scrapy.Field()  #
    content = scrapy.Field()  #
    state = scrapy.Field()  #
    image_url = scrapy.Field()  #
    title = scrapy.Field()  #
    can_comment = scrapy.Field()  #
    type = scrapy.Field()  #
    suggest_edit = scrapy.Field()  #

    def __str__(self):
        return f"文章ID: {self.id}, 标题: {self.title}"
