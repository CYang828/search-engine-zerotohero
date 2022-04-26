# -*- coding: utf-8 -*-
# @Time    : 2022/3/4 4:01 下午
# @Author  : zhengjiawei
# @FileName: processing.py
# @Software: PyCharm
import json
import os
import re
from collections import defaultdict, Counter

import happybase
import redis
from tqdm import tqdm


def replace_with_separator(text, separator, regexs):
    replacement = r"\1" + separator + r"\2"
    result = text
    for regex in regexs:
        result = regex.sub(replacement, result)
    return result


class SplitSentence:
    def __init__(self):
        self.SEPARATOR = r'@'
        self.RE_SENTENCE = re.compile(r'(\S.+?[.!?])(?=\s+|$)|(\S.+?)(?=[\n]|$)', re.UNICODE)
        self.AB_SENIOR = re.compile(r'([A-Z][a-z]{1,2}\.)\s(\w)', re.UNICODE)
        self.AB_ACRONYM = re.compile(r'(\.[a-zA-Z]\.)\s(\w)', re.UNICODE)
        self.UNDO_AB_SENIOR = re.compile(r'([A-Z][a-z]{1,2}\.)' + self.SEPARATOR + r'(\w)', re.UNICODE)
        self.UNDO_AB_ACRONYM = re.compile(r'(\.[a-zA-Z]\.)' + self.SEPARATOR + r'(\w)', re.UNICODE)

    def run(self, data):
        return self.split_sentence(data)

    def split_sentence(self, text, best=True):
        text = re.sub('([。！？\?])([^”’])', r"\1\n\2", text)
        text = re.sub('(\.{6})([^”’])', r"\1\n\2", text)
        text = re.sub('(\…{2})([^”’])', r"\1\n\2", text)
        text = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', text)
        for chunk in text.split("\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            if not best:
                yield chunk
                continue
            processed = replace_with_separator(chunk, self.SEPARATOR, [self.AB_SENIOR, self.AB_ACRONYM])
            for sentence in self.RE_SENTENCE.finditer(processed):
                sentence = replace_with_separator(sentence.group(), r" ",
                                                  [self.UNDO_AB_SENIOR, self.UNDO_AB_ACRONYM])
                yield sentence


def get_split_sentences(data):
    split_sentence = SplitSentence()
    data_new = defaultdict(list)
    for key, value in data.items():
        if key == 'title':
            data_new[key].extend(data[key])
        else:
            sentences_list = []
            for sentences in data[key]:
                for each in split_sentence.run(sentences):
                    sentences_list.append(each)
            data_new[key].extend(sentences_list)
    return data_new


def read_data(hbase_url="10.30.89.124", hbase_port=9090):
    connection = happybase.Connection(host=hbase_url, port=hbase_port,
                                      timeout=100000)
    table = connection.table('document_features_02')
    data = defaultdict(list)
    for i, each in enumerate(table.scan(batch_size=10)):
        title = each[1][b'document:title'].decode()
        summary = each[1][b'document:excerpt'].decode()
        content = each[1][b'document:clean_content'].decode()
        data['title'].append(title)
        data['summary'].append(summary)
        data['content'].append(content)
    return data


def save_corpus(redis_url="10.30.89.124", redis_port=6379):
    data = read_data()
    data = get_split_sentences(data)
    res = redis.StrictRedis(host=redis_url, port=redis_port, db=0)
    res.set('sentences', json.dumps(data))


def generate_data(data, corpus_file_path):
    with open(corpus_file_path, 'w', encoding='utf8') as f:
        for row in tqdm(data, total=len(data)):
            f.write(row + '\n')


def generate_vocab(total_data, vocab_file_path):
    total_tokens = [token for sent in total_data for token in sent]
    counter = Counter(total_tokens)
    vocab = [token for token, freq in counter.items()]
    vocab = ['[PAD]', '[UNK]', '[CLS]', '[SEP]', '[MASK]'] + vocab
    with open(vocab_file_path, 'w', encoding='utf8') as f:
        f.write('\n'.join(vocab))


def main():
    save_corpus()
    corpus_file_path = 'recall/bert_wwm_pretrain/data/pretrain_corpus.txt'
    vocab_file_path = 'recall/bert_wwm_pretrain/data/vocab.txt'
    redis_url = "10.30.89.124"
    redis_port = 6379
    res = redis.StrictRedis(host=redis_url, port=redis_port, db=0)
    data = json.loads(res.get('sentences'))
    data_list = []
    for each in data.keys():
        data_list.extend(data[each])
    #
    generate_data(data_list, corpus_file_path)
    generate_vocab(data_list, vocab_file_path)


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    # main()
    word_list = []
    with open('recall/bert_wwm_pretrain/data/vocab.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip('\n')
            word_list.append(line)
    print('len(word_list):', len(word_list))
    new_word_list = []
    with open('recall/bert_wwm_pretrain/data/chinese_bert_wwm/vocab.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip('\n')
            new_word_list.append(line)
    print('len(new_word_list):', len(new_word_list))
