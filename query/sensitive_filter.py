# -*- coding:utf-8 -*-
# @Time   :2021/12/17 5:48 下午
# @Author :Mengqi Li
# @FileName:sensitive_filter.py
# coding=utf-8
from collections import defaultdict
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DFA算法
class DFAFilter:
    """
    从关键字中过滤敏感词
    使用确定性有限自动机（DFA）减少更换时间
    """

    def __init__(self):
        # 关键词链表
        self.keyword_chains = {}
        # 限定
        self.delimit = "\x00"
        self.parse(BASE_DIR + "/query/model_data/sensitive-words/sensitive.txt")

    def add(self, keyword):
        # 关键词英文变为小写
        keyword = keyword.lower()
        # 关键字去除首尾空格和换行
        chars = keyword.strip()
        # 如果关键词为空直接返回
        if not chars:
            return
        level = self.keyword_chains
        # 遍历关键词的每个字
        for i in range(len(chars)):
            # 如果这个字已经存在字符链的key中就进入其子字典
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    # 新出现的给新出现的字赋值为一个空字典{}
                    level[chars[j]] = {}
                    # 记录最后一个字和
                    last_level, last_char = level, chars[j]
                    # level指向最后一层空字典
                    level = level[chars[j]]
                # 把最后一个字对应的value赋值为{'\x00': 0}
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding="utf-8") as f:
            for keyword in f:
                self.add(str(keyword).strip())
        # print(self.keyword_chains)

    def filter(self, message, repl=""):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    # 如果没有出现结束符号delimit，继续匹配
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        # 如果不是敏感字，则跳出循环，并把下标前移一位
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1
        return "".join(ret)


class BSFilter:
    """
    从关键字过滤消息
    使用反向排序映射来减少替换时间
    """

    def __init__(self):
        self.keywords = []
        self.kwsets = set([])
        self.bsdict = defaultdict(set)
        self.pat_en = re.compile(r"^[0-9a-zA-Z]+$")

    def add(self, keyword):
        if not isinstance(keyword, str):
            keyword = keyword.decode("utf-8")
        keyword = keyword.lower()
        if keyword not in self.kwsets:
            self.keywords.append(keyword)
            self.kwsets.add(keyword)
            index = len(self.keywords) - 1
            for word in keyword.split():
                if self.pat_en.search(word):
                    self.bsdict[word].add(index)
                else:
                    for char in word:
                        self.bsdict[char].add(index)

    def parse(self, path):
        with open(path, "r") as f:
            for keyword in f:
                self.add(keyword.strip())

    def filter(self, message, repl="*"):
        if not isinstance(message, str):
            message = message.decode("utf-8")
        message = message.lower()
        for word in message.split():
            if self.pat_en.search(word):
                for index in self.bsdict[word]:
                    message = message.replace(self.keywords[index], repl)
            else:
                for char in word:
                    for index in self.bsdict[char]:
                        message = message.replace(self.keywords[index], repl)
        return message


if __name__ == "__main__":
    gfw = DFAFilter()
    path = "model_data/sensitive-words/sensitive.txt"
    gfw.parse(path)
    text = "你真是个大傻逼，大傻子，傻大个，大坏蛋，坏人。"
    # text = "野营刀具军品网"
    result = gfw.filter(text)
    print(text)
    print(result)
    # if text == result:
    #     print("ok")
    # else:
    #     print("not ok")

    # bsf = BSFilter()
    # bsf.parse(path)
    # result = bsf.filter(text)
    # print(result)
