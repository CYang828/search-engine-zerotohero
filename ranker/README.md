# 读入数据
(1)从csv 文件中读入数据(完成)  

(2)从hive中读取数据  
# 构建推荐模型

对于单个预测任务使用deepfm

# 使用MMoE
https://pic3.zhimg.com/80/v2-b5f197829de0d34af55029f76dbfb6c2_1440w.png

使用deepfm或者xdeepfm作为expert模块

为每个任务都配备一个 Gate 模型。对于不同的任务，特定的 Gate k 的输出表示不同
的 Expert 被选择的概率，将多个 Expert 加权求和，得到f^k(x) ，并输出给特定的
 Tower 模型，用于最终的输出。
 
由于DeepCTR库中的deepfm在训练模型的时候，需要把全部数据传递给模型，
但在数据量特别大的情况下，特别容易内存爆炸，所以需要自己重新搭建
deepfm模型或者xdeepfm模型

deepfm模型主要由两部分组成，fm层和dnn层(直接从DeepCTR库中进行copy)


xdeepfm模型主要由两部分组成，cin部分和dnn部分 (直接从DeepCTR库中进行copy)       
  
xdeepfm模型中cin部分的输入纬度(bs, num_field, emb_size)






xdeepfm模型中cin部分的输入纬度(bs, num_field, emb_size)

dnn的输入是将稀疏变量和稠密变量进行拼接之后传入
sparse_embeddings_list是[num_field个,(bs,emb_size)]
sparse_dnn_input = torch.flatten(torch.cat(sparse_embeddings_list, dim=-1), start_dim=1)
dense_dnn_input = torch.stack(dense_values_list, dim=-1)
dnn_input = torch.cat([sparse_dnn_input, dense_dnn_input], dim=1) # bs num_field*emb_size+num_dense

进行batch_norm之后输入dnn网络



xdeepfm作为mmoe中的expert模块

mmoe中的gate模块 输入是所有的变量将稀疏和稠密变量拼接在一起作为输入(bs，nums_feature)
mmoe中的tower模块



deepfm模型中fm层其实是由两部分组成，一个是线性层部分，一个是数学中的fm，做特征交叉
线性层的是离散变量经过embedding之后记为x1,联系变量记为x2
线性层linear = x1 w1+x2 w2
fm部分 主要解决稀疏数据下的特征组合问题，所以传入是稀疏变量经过embedding之后的变量sparse_embedding_list

dnn层的输入是sparse_embedding_list和稠密变量拼接在一起作为输入[bs,num_dense+num_sparse*embedding_dim]





