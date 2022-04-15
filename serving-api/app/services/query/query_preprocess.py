# -*- coding:utf-8 -*-
# @Time   :2022/1/27 3:36 下午
# @Author :Li Meng qi
# @FileName:query_preprocess.py
import opencc
import re


class QueryPre:
    def __init__(self):
        pass

    def strQ2B(self, ustring):
        """把字符串全角转半角"""
        rstring = ""
        for uchar in ustring:
            inside_code = ord(uchar)  # ord返回对应的ascii数值，
            if inside_code == 12288:  # 全角空格直接转换
                inside_code = 32
            elif inside_code >= 65281 and inside_code <= 65374:  # 全角字符（除空格）根据关系转化
                inside_code -= 65248
            rstring += chr(inside_code)
        return rstring

    def strB2Q(self, ustring):
        """把字符串半角转全角"""
        rstring = ""
        for uchar in ustring:
            inside_code = ord(uchar)  # ord返回对应的ascii数值，
            if inside_code == 32:  # 半角空格直接转换
                inside_code = 12288
            elif inside_code >= 33 and inside_code <= 126:
                inside_code += 65248
            rstring += chr(inside_code)  # chr输入一个整数返回其对应的ascii字符
        return rstring

    def capital_to_lower(self, ustring):
        """
         大写转小写
        :param ustring: 字符串
        :return: 所有字母都小写后的字符串
        """
        return ustring.lower()

    def t2s_by_opencc(self, ustring):
        """
        繁体转简体
        :param ustring: 繁体string
        :return: 简体string
        """
        return opencc.OpenCC("t2s.json").convert(ustring)

    def filter_emoji(self, desstr, restr=""):
        """
        清除表情
        :param desstr: 需要过滤的字符串
        :param restr: 被替换成什么字符
        :return: 返回处理结果
        """
        # 过滤表情
        try:
            co = re.compile("[\U00010000-\U0010ffff]")
        except re.error:
            co = re.compile("[\uD800-\uDBFF][\uDC00-\uDFFF]")
        return co.sub(restr, desstr)
