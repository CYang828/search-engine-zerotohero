# 文章特征提取

------

## 一、功能

对存放在mongodb中的数据进行数据整理和文本特征建设并将整理后的数据和特征存入到hbase中，其中特征建设包括分词、命名实体识别、关键词提取和文本向量化表示，分词和实体识别借助Hnalp工具；关键词提取借助jieba工具，采用textRank算法；文本向量化采用bert进行编码。

features_utils.py文件中封装了如下工具方法：分词、实体识别、清洗HTML标签、基于规则的分句、文本向量化、词向量提取（该功能目前版本还未用到）。

main.py中对整个流程进行实现。

## 二、启动

注：在安装了本项目需要的所有包之后按照如下步骤启动程序：

1、下载bert中文预训练模型，下载地址：https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip

2、解压缩下载的文件。

3、运行命令bert-serving-start -model_dir chinese_L-12_H-768_A-12 -num_worker=1 -max_seq_len 512 启动bert编码服务器。-model_dir：预训练模型保存路径 -num_worker：启动服务指定的线程数量 -max_seq_len：编码句子的最大长度

4、python main.py

## 三、必要的包与版本

hanlp==2.1.0

happybase==1.2.0

jieba==0.42.1

pymongo==3.12.1

tensorflow==1.14.0

bert-serving-client==1.10.0

bert-serving-server==1.10.0

gensim==4.1.2