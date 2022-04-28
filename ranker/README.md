### 执行步骤：  
(1)模拟生成数据(具体逻辑可以在dataset/README.md中查看)  
python -m dataset.sampler.main  
(2)进行精排训练  
python -m ranker.src.train  

###精排逻辑
使用MMOE同时对是否点击，点赞，评论进行预测,MMOE的except模块使用xdeepfm，
同时由于DeepCTR_pytorch库中xdeepfm在训练时要求加载所有的数据，
所以当数据量很大时，内存容易爆炸，所以对xdeepfm重新构造
(1)构造xdeepfm模型的组件CIN，DNN，Linear和xdeepfm模型(Expert)  
(2)构造MMOE(MultiDeepFM)，其实应该是MultiXDeepFM  
(3)读入数据构造Dataset，dataloader  
(4)train函数和评估函数  

# 使用分布式
horovod安装：     
可以直接使用docker ,镜像名：horovod/horovod:latest  

pytorch版本 使用教程 https://github.com/horovod/horovod/blob/master/docs/pytorch.rst
因为数据量不是特别大,速度优势没有体现出来，但比普通的torch.nn.DataParallel效果好很多






