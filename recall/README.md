# 召回
------
## 一、文本召回


## 二、向量召回

1、将mongodb中的所有文本数据进行提取，将每篇文章的title、summary、content合并成形成新的数据\
2、构建dataset,dataloader\
3、构建模型MLM\
4、模型训练\
5、根据训练好的模型，得到title向量，summary向量和content向量\
6、将得到的向量保存在hbase中\
7、使用title_vector_recall、summary_vector_recall、content_vector_recall中的函数进行向量召回\\