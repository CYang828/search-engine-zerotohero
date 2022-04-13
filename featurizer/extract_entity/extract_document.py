# -*- coding:utf-8 -*-
# @Time   :2022/2/28 5:08 下午
# @Author :Li Meng qi
# @FileName:extract_document.py
from feature_utils.clean_html_tag import CleanHtmlTag
from extract_entity import BaseExtract
from entity.document import Document
import json
import jieba.analyse as analyse


class ExtractDocument(BaseExtract):
    def __init__(self, textvector, hanlptokensner):

        self.extract_article = CleanHtmlTag()
        # self.document_vector = TextVector()
        self.hanlp_token_and_ner = hanlptokensner
        self.document_vector = textvector

    def extract(self, row_data):
        document = Document()
        one_data = row_data
        document.title = one_data['title']  # title文章标题
        document.content = one_data['content']  # content正文内容
        document.excerpt = one_data['excerpt']  # excerpt文章前面的若干文字内容
        document.type = one_data['type']  # type	文章类型
        document.image_url = one_data['image_url']  # image_url文章的封面图片地址链接
        document.created = str(one_data['created'])  # created文章创建时间戳
        document.updated = str(one_data['updated'])  # updated文章更新时间戳
        document.id = str(one_data['id'])  # id知乎编码的文章id
        document.has_column = str(one_data['has_column'])  # has_column专栏收录
        # tokens	文章的分词结果
        # entity	文章中出现的人名、地名、机构名等
        # 标题、文章、摘要的文本向量表示;清洗后的正文内容;
        # document:clean_content、document:title_vector、document:clean_content_vector、document:excerpt_vector
        clean_content = self.extract_article.run(one_data['content'])
        if clean_content.strip() == '':
            document.clean_content = clean_content
            document.title_vector = json.dumps({'title_vector': []})
            document.clean_content_vector = json.dumps({'clean_content_vector': []})
            document.excerpt_vector = json.dumps({'excerpt_vector': []})
            document.tokens = json.dumps({'tok_fine': []})
            document.entity = json.dumps({})
            document.top5words = json.dumps({'top5word': []})
            print('文章内容是空:', document.clean_content)
            return document
        document.clean_content = clean_content
        try:
            if one_data['title'].strip() != '':
                document.title_vector = json.dumps(
                    {'title_vector': self.document_vector.run(one_data['title'])})
            else:
                document.title_vector = json.dumps({'title_vector': []})
        except Exception as e:
            print(e)
            document.title_vector = json.dumps({'title_vector': []})

        document.clean_content_vector = json.dumps(
            {'clean_content_vector': self.document_vector.run(clean_content)})
        if one_data['excerpt'].strip() != '':
            document.excerpt_vector = json.dumps(
                {'excerpt_vector': self.document_vector.run(one_data['excerpt'])})
        else:
            document.excerpt_vector = json.dumps(
                {'excerpt_vector': []})

        try:
            document_tokens, document_entity = self.hanlp_token_and_ner.run(clean_content)  # 使用hanlp工具进行分词和实体识别
            document_top5words = analyse.textrank(clean_content, topK=5, withWeight=False,
                                                  allowPOS=('ns', 'n', 'vn', 'v'))  # 从ns地名，n名词，vn名动词， v动词这些词性中提取关键词
            document.tokens = document_tokens
            document.entity = document_entity
            document.top5words = json.dumps({'top5word': document_top5words})
        except Exception as e:
            print('分词 or 实体识别 or top5w时出错')
            print(e)
            print('出错文章:{}'.format(len(clean_content)))
            document.tokens = json.dumps({'tok_fine': []})
            document.entity = json.dumps({})
            document.top5words = json.dumps({'top5word': []})
        return document
