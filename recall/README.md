召回
------
在根目录下 执行
python -m recall.recall

### 召回部分的目录结构
|-- text_recall  
|   |-- __init__.py  
|   -- text_recall.py  # 文本召回    
|-- vector_data # 存储向量召回时的向量数据    
|-- vector_recall  
|   |-- __init__.py  
|   |-- content_vector_recall.py  # 使用query和文章内容向量进行召回    
|   |-- summary_vector_recall.py  # 使用query和文章摘要向量进行召回    
|   |-- title_vector_recall.py    # 使用query和文章标题向量进行召回    
|   -- vector_recall.py         #向量召回    
|-- README.md  
|-- __init__.py              #定义了BaseRecall,并调用了config.ini中的参数  
|-- main.py                     # 召回  
|-- utils.py  



## 一、文本召回  
 使用python 连接es时，注意版本要求  
 
 pip install elasticsearch==7.5.1  
 
 1、将es查询结果进行解析，并获得命中的文章id(结果为list)
 
 python -m recall.text_recall.text_recall
 
 
 
## 二、向量召回  

python -m recall.vector_recall.vector_recall  

### 实现步骤
### 2.0 对查询字符串进行embedding
(1)将要查询的字符串使用bert进行向量编码 获得query_array
### 2.1 title vector recall
(2)将所有文章的标题(title)转换成向量保存在pickle文件中  
(3)使用faiss加载pickle文件中的向量  
(4)将query_array放入到faiss中查询并获得距离近的文章id(也就是根据title向量召回的文章id)  
python -m recall.vector_recall.title_vector_recall  

### 2.2 summary vector recall
(2)将所有文章的摘要(summary)转换成向量保存在pickle文件中  
(3)使用faiss加载pickle文件中的向量  
(4)将query_array放入到faiss中查询并获得距离近的文章id(也就是根据summary向量召回的文章id))  
python -m recall.vector_recall.summary_vector_recall  

### 2.3 content vector recall
python -m recall.vector_recall.content_vector_recall  
(2)将所有文章的内容(content)转换成向量保存在pickle文件中  
(3)使用faiss加载pickle文件中的向量  
(4)将query_array放入到faiss中查询并获得距离近的文章id(也就是根据content向量召回的文章id))  

## 三、召回(向量和文本召回)

将文本召回和向量召回的结果放在一个列表中返回
python -m recall.main

## 四、进行evaluation

(1)从样本中采样5w个样本作为test数据集  
(2)去除其中搜索内容为空的样本作为新的test数据集  
(3)评估根据每个样本中的搜索内容返回的召回列表中，是否包含样本的文章id(是否包含点击的文章)  
包含记为1，不包含记为0(召回列表包含样本文章id简称命中)(使用多线程完成)  
(4)hit_rate = 所有样本中命中的数量/样本量  

python -m recall.evaluation

TODO
使用bulk对es进行批量查询  
faiss进行批量查询  
对多个样本进行多进程召回(dask)  
