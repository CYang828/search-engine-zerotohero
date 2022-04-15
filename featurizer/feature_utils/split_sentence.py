# -*- coding:utf-8 -*-
# @Time   :2022/2/24 4:50 下午
# @Author :Li Meng qi
# @FileName:split_sentence.py
from feature_utils import FeatureBase
import re

SEPARATOR = r"@"
RE_SENTENCE = re.compile(r"(\S.+?[.!?])(?=\s+|$)|(\S.+?)(?=[\n]|$)", re.UNICODE)
AB_SENIOR = re.compile(r"([A-Z][a-z]{1,2}\.)\s(\w)", re.UNICODE)
AB_ACRONYM = re.compile(r"(\.[a-zA-Z]\.)\s(\w)", re.UNICODE)
UNDO_AB_SENIOR = re.compile(r"([A-Z][a-z]{1,2}\.)" + SEPARATOR + r"(\w)", re.UNICODE)
UNDO_AB_ACRONYM = re.compile(r"(\.[a-zA-Z]\.)" + SEPARATOR + r"(\w)", re.UNICODE)


class SplitSentence(FeatureBase):
    def run(self, data):
        return self.split_sentence(data)

    def split_sentence(self, text, best=True):
        text = re.sub("([。！？\?])([^”’])", r"\1\n\2", text)
        text = re.sub("(\.{6})([^”’])", r"\1\n\2", text)
        text = re.sub("(\…{2})([^”’])", r"\1\n\2", text)
        text = re.sub("([。！？\?][”’])([^，。！？\?])", r"\1\n\2", text)
        for chunk in text.split("\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            if not best:
                yield chunk
                continue
            processed = self.replace_with_separator(
                chunk, SEPARATOR, [AB_SENIOR, AB_ACRONYM]
            )
            for sentence in RE_SENTENCE.finditer(processed):
                sentence = self.replace_with_separator(
                    sentence.group(), r" ", [UNDO_AB_SENIOR, UNDO_AB_ACRONYM]
                )
                yield sentence

    def replace_with_separator(self, text, separator, regexs):
        replacement = r"\1" + separator + r"\2"
        result = text
        for regex in regexs:
            result = regex.sub(replacement, result)
        return result


# if __name__ == '__main__':
#     data = """
#     语法上指复句里划分出来的相当于单句的部分。分句和分句之间一般有停顿，在书面上用逗号或分号表示。分句之间在意义上有一定的联系，常用一些关联词语来连接。如“只要我们共同努力，我们的任务就一定能完成”这个复句，就是由两个分句组成的。
#     """
#     splitsentence = SplitSentence()
#     for sentence in splitsentence.run(data):
#         print(sentence)
