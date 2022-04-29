## 训练步骤  
### 1、生成训练语料和vocab.txt文件
(1)从数据库中读取数据  
(2)将数据切分成句子保存在pretrain_corpus.txt文件中(同时保存在了redis中,可以选择性使用)  
(3)生成vocab.txt文件(和bert使用的vocab.txt格式保持一致)

python -m public.bert_wwm_pretrain.processing 

### 2、开始训练
(1)在https://huggingface.co/hfl/chinese-bert-wwm/tree/main下载vocab.txt、config.json
和pytorch_model.bin文件并保存在public/bert_wwm_pretrain/data/chinese_bert_wwm目录下  
(2) 执行main函数
有条件的同学可以多使用几个GPU  
python -m public.bert_wwm_pretrain.train

## whole word mask逻辑
bert是针对字进行训练，whole word mask同样是针对字进行训练，
那么是如何哪些字的组合是一个词，并且对其mask。
并且这一步选择在Collator中实现。
关于Collator和dataset,dataloader,sampler之间的关系可以参考：
https://zhuanlan.zhihu.com/p/402666821  
[Collator 官方 API 文档](https://huggingface.co/docs/transformers/main_classes/data_collator)

看一下具体实现步骤：
(1)先获得这个批次数据的最大长度max_seq_len
(2)对句子进行补齐和截断
(3)对于每个样本的input_ids,随机选择要mask的字(token)  
(4)在对应的token前添加特殊符号##比如 4 -> ##4
(5)将带特征符号##的token和前一个token进行mask标记获得mask_label
(6)根据mask_label和input_ids进行mask(80%进行mask掉，10%进行随机替换，10选择保持不变)





