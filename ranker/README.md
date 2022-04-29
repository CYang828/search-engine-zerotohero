### 执行步骤：  
(1)模拟生成数据(具体逻辑可以在dataset/README.md中查看)  
python -m dataset.sampler.main  
(2)进行精排训练
使用horovod分布式之后不能使用 python -m ranker.src.train 进行训练

执行代码：
```bash
CUDA_VISIBLE_DEVICES=1,3  horovodrun -np 2 -H localhost:2 --gloo python -m ranker.src.train
````
CUDA_VISIBLE_DEVICES=1,3指定使用的GPU型号，-np 指的是进程的数量，localhost:2表示localhost节点上2个GPU。  
并且一个卡一个进程，意味着localhost:2不能超过-np 2的数量(或许有其他使用方法，但还没找到)  


###精排逻辑
使用MMOE同时对是否点击，点赞，评论进行预测,MMOE的except模块使用xdeepfm，
同时由于DeepCTR_pytorch库中xdeepfm在训练时要求加载所有的数据，
所以当数据量很大时，内存容易爆炸，所以对xdeepfm重新构造  
(1)构造xdeepfm模型的组件CIN，DNN，Linear和xdeepfm模型(Expert)  
(2)构造MMOE(MultiDeepFM)，其实应该是MultiXDeepFM  
(3)读入数据构造Dataset，dataloader  
(4)train函数和评估函数  

### 使用分布式
horovod安装：     
可以直接使用docker ,镜像名：horovod/horovod:latest  

pytorch版本 使用教程 https://github.com/horovod/horovod/blob/master/docs/pytorch.rst  
如果想要了解原理的，可以参考以下几篇文章:  
(1)[深度学习分布式训练框架 Horovod (1) --- 基础知识](https://www.cnblogs.com/rossiXYZ/p/14856464.html)    
(2)[深度学习分布式训练框架 horovod (2) --- 从使用者角度切入](https://www.cnblogs.com/rossiXYZ/p/14856464.html)  
(3)[深度学习分布式训练框架 horovod (3) --- Horovodrun背后做了什么](https://www.cnblogs.com/rossiXYZ/p/14881812.html)  





