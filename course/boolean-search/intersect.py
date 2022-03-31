# -*- coding:utf-8 -*-
# @Time   :2022/3/29 10:58 上午
# @Author :Li Meng qi
# @FileName:intersect.py
from collections import defaultdict


# 实现intersect算法，时间算法复杂度O(n)
def intersect(p1, p2):
    answer = []
    p1_index = 0
    p2_index = 0
    while p1_index < len(p1) and p2_index < len(p2):
        if p1[p1_index] == p2[p2_index]:
            answer.append(p1[p1_index])
            p1_index += 1
            p2_index += 1
        elif p1[p1_index] < p2[p2_index]:
            p1_index += 1
        else:
            p2_index += 1
    return answer


def intersect_terms(*args):
    # 根据postings list的大小排序
    # 由小到大排序，减少比对次数
    terms = sorted(args, key=lambda x: len(x), reverse=False)
    # 取出最短的
    restlt = terms[0]
    terms = terms[1:]
    while len(terms) != 0 and len(restlt) != 0:
        restlt = intersect(restlt, terms[0])
        terms = terms[1:]
    return restlt


# build term-document matrix
def term_document_incidence(documents):
    term_document = []
    for i, doc in enumerate(documents):
        for token in doc.split():
            term_document.append((token, i + 1))
    return term_document


# sort term-document matrix by alphabet
def sort_by_alphabet(term_document):
    return sorted(term_document, key=lambda x: x[0])


# print matrix
def print_matrix(**kwargs):
    if kwargs['name'] == 'tdi':
        print('%-13s%10s' % ('term', 'docID'))
        for word, doc_id in kwargs['datas']:
            print('%-13s%10s' % (word, str(doc_id)))
    else:
        # term_fre=term_fre, term_postings_lists
        term_fre = kwargs['term_fre']
        print('%-13s%-10s%-10s' % ('term', 'doc.freq', 'pstings_lists'))
        for word, doc_id in kwargs['term_postings_lists'].items():
            print('%-13s%-10s%-10s' % (word, term_fre[word], str(doc_id)))


# build term document frequence and postings lists
def build_fre_poslists(datas):
    term_postings_set = defaultdict(set)
    for token, doc_id in datas:
        term_postings_set[token].add(doc_id)
    # 此处需要对每个terms对应的postings lists进行排序（由小到大），这样可以借助intersect算法使得查询速度相当高效
    term_postings_lists = defaultdict(list)
    for token, pos_set in term_postings_set.items():
        term_postings_lists[token] = sorted(pos_set, key=lambda x: x, reverse=False)
    term_fre = defaultdict(int)
    for token, pos_lists in term_postings_lists.items():
        term_fre[token] = len(pos_lists)
    return term_fre, term_postings_lists


if __name__ == '__main__':
    # 文档列表
    # 第1题
    documents = ['breakthrough drug for schizophrenia',
                 'new schizophrenia drug',
                 'new approach for treatment of schizophrenia',
                 'new hopes for schizophrenia patients']
    # a.Draw the term-document incidence matrix for this document collection.
    term_document = term_document_incidence(documents)
    print_matrix(datas=term_document, name='tdi')
    term_document = sort_by_alphabet(term_document)
    print_matrix(datas=term_document, name='tdi')
    # b.Draw the inverted index representation for this collection
    term_fre, term_postings_lists = build_fre_poslists(term_document)
    print_matrix(term_fre=term_fre, term_postings_lists=term_postings_lists, name='bfp')

    # 第2题
    p1 = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13]
    p2 = [3, 4, 5, 6, 8]
    p3 = [6, 8]
    p4 = [7, 8]
    print(intersect_terms(p1, p2, p3, p4))
    """
    分析：

    a.Brutus AND NOT Caesar
        
    b.Brutus OR NOT Caesar

    """



