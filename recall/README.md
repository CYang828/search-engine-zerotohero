# 召回
------
python -m recall.recall

### 召回部分的目录结构
|-- text_recall  
|   |-- __init__.py  
|   -- text_recall.py # 文本召回  
|-- vector_data # 存储向量召回时的向量数据  
|-- vector_recall  
|   |-- __init__.py  
|   |-- content_vector_recall.py # 使用query和文章内容向量进行召回  
|   |-- summary_vector_recall.py # 使用query和文章摘要向量进行召回  
|   |-- title_vector_recall.py  # 使用query和文章标题向量进行召回  
|   -- vector_recall.py  #向量召回  
|-- README.md  
|-- __init__.py  
|-- recall.py  
`-- utils.py  



## 一、文本召回  
 使用python 连接es时，注意版本要求  
 pip install elasticsearch==7.5.1  
 
 python -m recall.text_recall.text_recall
 
 
 
## 二、向量召回  

python -m recall.vector_recall.vector_recall  

### 2.1 title vector recall
python -m recall.vector_recall.title_vector_recall

### 2.2 summary vector recall
python -m recall.vector_recall.summary_vector_recall

### 2.3 content vector recall
python -m recall.vector_recall.content_vector_recall
