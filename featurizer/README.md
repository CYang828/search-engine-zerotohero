# 文章特征提取

------

## 一、功能

对存放在mongodb中的数据进行数据整理和文本特征建设并将整理后的数据和特征存入到hbase中，其中特征建设包括分词、命名实体识别和关键词提取，分词和实体识别借助Hnalp工具；关键词提取借助jieba工具，采用textRank算法。

data 中存放再训练的bert模型参数
entity 文件中定义了所有的实体类
extract_entity 文件中封装了对各个实体的特征抽取过程
features_utils 文件中封装了如下工具方法：分词、实体识别、清洗HTML标签、基于规则的分句。

run_build_document.py 对文章进行特征建设
run_build_searchinfo.py 对搜索信息进行特征建设
run_build_user.py 对用户信息进行特征建设

## 二、启动
### 1.数据准备与环境安装
```bash
pip install -r requirements.txt
# 下载语义 Bert 模型，解压缩模型文件
wget -P data/ http://aimaksen.bslience.cn/best_model_ckpt.zip
unzip data/best_model_ckpt.zip -d data/
# 下载搜索行为数据
wget -P data/ http://aimaksen.bslience.cn/search_information.csv
# 下载用户信息数据
wget -P data/ http://aimaksen.bslience.cn/user_data.csv
```
### 2.数据库参数配置
在config.ini中配置存储爬虫数据[mongo]与hbase特征平台[document_hbase]中的参数

### 3.特征构建
在项目根目录下依次执行下列语句来完成对文档、搜索信息和用户特征的构建与入库
```bash
python -m featurizer.run_build_document # 完成文章级别的特征建设
python -m featurizer.run_build_searchinfo # 完成搜索内容特征的建设
python -m featurizer.run_build_user # 完成用户特征的建设
```


## 三、必要的包与版本

hanlp==2.1.0a64

happybase==1.2.0

jieba==0.42.1

pymongo==3.12.1

PyHive==0.6.5
