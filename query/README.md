# query理解

------

## 一、功能

本部分是query的一些处理流程，实现了分词、实体识别、纠错、归一、扩展、脱敏、联想和term分析等功能。

## 二、启动

```bash
pip install -r requirements.txt
# 下载macbert纠错模型参数并解压
wget -P model_data/ http://xbot.bslience.cn/macbert4csc-base-chinese.zip
unzip model_data/macbert4csc-base-chinese.zip -d model_data/
# 下载腾讯词向量与使用Annoy创建的索引文件并解压
wget -P model_data/ http://xbot.bslience.cn/tencent-AILab-ChineseEmbedding.zip
unzip model_data/tencent-AILab-ChineseEmbedding.zip -d model_data/
# 下载无监督SVD意图识别生成的模型文件
wget -P model_data/ http://xbot.bslience.cn/intent-recognition.zip
unzip model_data/intent-recognition.zip -d model_data/
# 下载根据爬取的语料建设的字典文件
wget -P model_data/ http://xbot.bslience.cn/vocab_dic.bin
# 下载保存的语言模型文件
wget -P model_data/ http://xbot.bslience.cn/kilgariff_ngram_model.pkl
# 下载可以用来训练语言模型的语料（语料来自hbase中文章正文分句分词后的结果）
wget -P model_data/ http://xbot.bslience.cn/sentences_tokens.pkl

```

## 三、提示

+ 可以通过更改utils/build_tencent_vector_index.py中的参数来生成自己词向量索引并应用，索引的建立是加快相似词的搜索速度
+ 可自己往model_data/sensitive-words/sensitive.txt中追加敏感词来扩充敏感词表
+ query归一与query拓展等功能还有很大的优化空间，将在后续迭代中更新
+ 在utils/mle_model.py中提供了语言模型的训练代码，可以训练自己的语言模型


