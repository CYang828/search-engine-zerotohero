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

只需python 相应的py文件即可启动程序。

## 三、必要的包与版本

hanlp==2.1.0a64

happybase==1.2.0

jieba==0.42.1

pymongo==3.12.1

PyHive==0.6.5
