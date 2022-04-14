# -*- coding:utf-8 -*-
# @Time   :2022/3/8 3:40 下午
# @Author :Li Meng qi
# @FileName:association.py
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 开启
# CACHED = True
# 关闭
CACHED = False
# 注意，CACHED_SIZE >= search中的limit，保证search从缓存能获取到足够多的结果
CACHED_SIZE = 10
# 被搜索超过多少次后才加入缓存
CACHED_THREHOLD = 10


class Node(dict):
    def __init__(self, key, is_leaf=False, weight=0, kwargs=None):
        """
        @param key: 节点字符
        @param is_leaf: 是否叶子节点
        @param weight: 节点权重, 某个词最后一个字节点代表其权重，其余中间节点权重为0，无意义
        @param kwargs: 可传入其他任意参数，用于某些特殊用途
        """
        self.key = key
        self.is_leaf = is_leaf
        self.weight = weight
        # 缓存,存的是node指针
        self.cache = []
        # 节点前缀搜索次数，可以用于搜索query数据分析
        self.search_count = 0
        # 其他节点无关仅和内容相关的参数
        if kwargs:
            for key, value in kwargs.iteritems():
                setattr(self, key, value)

    def __str__(self):
        return '<Node key:%s is_leaf:%s weight:%s Subnodes: %s>' % (self.key, self.is_leaf, self.weight, self.items())

    def add_subnode(self, node):
        """
        添加子节点
        :param node: 子节点对象
        """
        self.update({node.key: node})

    def get_subnode(self, key):
        """
        获取子节点
        :param key: 子节点key
        :return: Node对象
        """
        return self.get(key)

    def has_subnode(self):
        """
        判断是否存在子节点
        :return: bool
        """
        return len(self) > 0

    def get_top_node(self, prefix):
        """
        获取一个前缀的最后一个节点(补全所有后缀的顶部节点)
        :param prefix: 字符转前缀
        :return: Node对象
        """
        top = self
        for k in prefix:
            top = top.get_subnode(k)
            if top is None:
                return None
        return top


class QueryAssociate:
    def __init__(self, file_path=BASE_DIR + '/query/model_data/query_association_data.txt'):
        self._build(file_path)

    def _add(self, node, keyword, weight=0, **kwargs):
        """
        加入一个单词到树
        @param node: 根节点
        @param keyword: 关键词，前缀
        @param weight: 权重
        @param kwargs: 其他任意存储属性
        """
        one_node = node
        index = 0
        last_index = len(keyword) - 1
        for c in keyword:
            if c not in one_node:
                if index != last_index:
                    one_node.add_subnode(Node(c, weight=weight))
                else:
                    one_node.add_subnode(Node(c, is_leaf=True, weight=weight, kwargs=kwargs))
                one_node = one_node.get_subnode(c)
            else:
                one_node = one_node.get_subnode(c)
                if CACHED:
                    one_node.cache = []
                if index == last_index:
                    one_node.is_leaf = True
                    one_node.weight = weight
                    for key, value in kwargs:
                        setattr(one_node, key, value)
            index += 1

    def delete(self, node, keyword, judge_leaf=False):
        """
        从树中删除一个单词
        @param node: 根节点
        @param keyword: 关键词，前缀
        @param judge_leaf: 是否判定叶节点，递归用,外部调用使用默认值
        """
        # 空关键词，传入参数有问题，或者递归调用到了根节点,直接返回
        if not keyword:
            return
        top_node = node.get_top_node(keyword)
        if top_node is None:
            return
        # 清理缓存
        if CACHED:
            top_node.cache = []
        # 递归往上，遇到节点是某个关键词节点时，要退出
        if judge_leaf:
            if top_node.is_leaf:
                return
        # 非递归，调用delete
        else:
            if not top_node.is_leaf:
                return
        if top_node.has_subnode():
            # 存在子节点，去除其标志 done
            top_node.is_leaf = False
            return
        else:
            # 不存在子节点，逐层检查删除节点
            this_node = top_node
            prefix = keyword[:-1]
            top_node = node.get_top_node(prefix)
            del top_node[this_node.key]
            self.delete(node, prefix, judge_leaf=True)

    def _build(self, file_path, is_case_sensitive=False):
        """
        从文件构建数据结构, 文件必须utf-8编码,可变更

        @param file_path: 数据文件路径，数据文件默认两列，格式“关键词\t权重"
        @param is_case_sensitive: 是否大小写敏感
        """
        node = Node("")
        f = open(file_path)
        for line in f:
            line = line.strip()
            if not isinstance(line, str):
                line = line.decode('utf-8')
            parts = line.split('\t')
            if len(parts) == 1:
                continue
            name = parts[0]
            if not is_case_sensitive:
                name = name.lower()
            #         print(parts)
            self._add(node, name, int(parts[1]))
        f.close()
        self.node = node

    def search(self, prefix, limit=None, is_case_sensitive=False):
        """
        搜索一个前缀下的所有单词列表 递归
        @param prefix: 前缀
        @param limit: 返回提示的数量
        @param is_case_sensitive: 是否大小写敏感
        @return: [(key, node)], 包含提示关键字和对应叶子节点的元组列表
        """
        if not is_case_sensitive:
            prefix = prefix.lower()
        node = self.node.get_top_node(prefix)
        # print 'len(node):' ,len(node)
        # 如果找不到前缀节点，代表匹配失败，返回空
        if node is None:
            return []
        # 搜索次数递增
        node.search_count += 1
        if CACHED and node.cache:
            return node.cache[:limit] if limit is not None else node.cache
        # print depth_walk(node)
        result = [(prefix + subkey, pnode) for subkey, pnode in self.depth_walk(node)]
        result.sort(key=lambda x: x[1].weight, reverse=True)
        if CACHED and node.search_count >= CACHED_THREHOLD:
            node.cache = result[:CACHED_SIZE]
        # print len(result)
        return result[:limit] if limit is not None else result

    def depth_walk(self, node):
        """
        递归，深度优先遍历一个节点,返回每个节点所代表的key以及所有关键字节点(叶节点)
        @param node: Node对象
        """
        result = []
        if node.is_leaf:
            # result.append(('', node))
            if len(node) > 0:  # 修改，避免该前缀刚好是关键字时搜索不到
                result.append((node.key[:-1], node))
                node.is_leaf = False
                self.depth_walk(node)
            else:
                return [('', node)]
        if node.has_subnode():
            for k in node.keys():
                s = self.depth_walk(node.get(k))
                # print k , s[0][0]
                result.extend([(k + subkey, snode) for subkey, snode in s])
            return result

if __name__ == '__main__':
    queryass = QueryAssociate()
    query = '学习'
    for key, node in queryass.search(query, limit=10):
        print(key, node.weight)