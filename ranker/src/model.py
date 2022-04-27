# -*- coding: utf-8 -*-
# @Time    : 2022/4/7 10:55 上午
# @Author  : zhengjiawei
# @FileName: model.py
# @Software: PyCharm

import torch
import torch.nn as nn
import torch.nn.functional as F
from argparse import Namespace
from collections import defaultdict
from ranker.src.activation import activation_layer
from ranker.src.utils import FocalLoss_MultiLabel
from typing import Dict


class DNN(nn.Module):
    """The Multi Layer Percetron

      Input shape
        - nD tensor with shape: ``(batch_size, ..., input_dim)``. The most common situation would be
        a 2D input with shape ``(batch_size, input_dim)``.

      Output shape
        - nD tensor with shape: ``(batch_size, ..., hidden_size[-1])``. For instance, for a 2D input
        with shape ``(batch_size, input_dim)``, the output would have shape ``(batch_size, hidden_size[-1])``.

      Arguments
        - **inputs_dim**: input feature dimension.

        - **hidden_units**:list of positive integer, the layer number and units in each layer.

        - **activation**: Activation function to use.

        - **l2_reg**: float between 0 and 1. L2 regularizer strength applied to the kernel weights matrix.

        - **dropout_rate**: float in [0,1). Fraction of the units to dropout.

        - **use_bn**: bool. Whether use BatchNormalization before activation or not.

        - **seed**: A Python integer to use as random seed.
    """

    def __init__(self, inputs_dim, hidden_units, activation='relu', l2_reg=0, dropout_rate=0, use_bn=False,
                 init_std=0.0001, dice_dim=3, seed=1024, device='cpu'):
        super(DNN, self).__init__()
        self.dropout_rate = dropout_rate
        self.dropout = nn.Dropout(dropout_rate)
        self.seed = seed
        self.l2_reg = l2_reg
        self.use_bn = use_bn
        if len(hidden_units) == 0:
            raise ValueError("hidden_units is empty!!")
        hidden_units = [inputs_dim] + list(hidden_units)

        self.linears = nn.ModuleList(
            [nn.Linear(hidden_units[i], hidden_units[i + 1]) for i in range(len(hidden_units) - 1)])

        if self.use_bn:
            self.bn = nn.ModuleList(
                [nn.BatchNorm1d(hidden_units[i + 1]) for i in range(len(hidden_units) - 1)])

        self.activation_layers = nn.ModuleList(
            [activation_layer(activation, hidden_units[i + 1], dice_dim) for i in range(len(hidden_units) - 1)])

        for name, tensor in self.linears.named_parameters():
            if 'weight' in name:
                nn.init.normal_(tensor, mean=0, std=init_std)

        self.to(device)

    def forward(self, inputs):
        deep_input = inputs

        for i in range(len(self.linears)):

            fc = self.linears[i](deep_input)

            if self.use_bn:
                fc = self.bn[i](fc)

            fc = self.activation_layers[i](fc)

            fc = self.dropout(fc)
            deep_input = fc
        return deep_input


class FM(nn.Module):
    """Factorization Machine models pairwise (order-2) feature interactions
     without linear term and bias.
      Input shape
        - 3D tensor with shape: ``(batch_size,field_size,embedding_size)``.
      Output shape
        - 2D tensor with shape: ``(batch_size, 1)``.
      References
        - [Factorization Machines](https://www.csie.ntu.edu.tw/~b97053/paper/Rendle2010FM.pdf)
    """

    def __init__(self):
        super(FM, self).__init__()

    def forward(self, inputs):
        fm_input = inputs
        square_of_sum = torch.pow(torch.sum(fm_input, dim=1, keepdim=True), 2)
        sum_of_square = torch.sum(fm_input * fm_input, dim=1, keepdim=True)
        cross_term = square_of_sum - sum_of_square
        cross_term = 0.5 * torch.sum(cross_term, dim=2, keepdim=False)

        return cross_term


def create_embedding_dict(config, linear=False):
    direct_emb = 4
    embedding_dict = nn.ModuleDict(
        {
            feat_name: nn.Embedding(feat_size, feat_emb_size if not linear else direct_emb)
            for (feat_name, feat_size, feat_emb_size)
            in config.sparse_feature_info
        }
    )
    for tensor in embedding_dict.values():
        nn.init.normal_(tensor.weight, mean=0, std=config.init_std)

    return embedding_dict


class Linear(nn.Module):

    def __init__(self, config):
        super(Linear, self).__init__()
        self.embedding_dict = create_embedding_dict(config, linear=False)
        self.weight = nn.Parameter(torch.Tensor(2, 3))
        self.trans_weight = nn.Parameter(torch.Tensor(60, 3))  # 60是离散变量的数量*映射的维度 6*10
        torch.nn.init.normal_(self.weight, mean=0, std=config.init_std)
        torch.nn.init.normal_(self.trans_weight, mean=0, std=config.init_std)

    def forward(self,
                dense_features: torch.Tensor,
                sparse_features: Dict[str, torch.Tensor],
                ):
        sparse_embeddings_dict = defaultdict(list)

        for feat_name, sparse_idx in sparse_features.items():
            if feat_name in ['gender', 'search_token']:
                # 性别是从0开始，其他类别变量都是从1开始，对应embedding中的索引要-1
                sparse_embeddings_dict[feat_name] = self.embedding_dict[feat_name](sparse_idx)
            else:
                sparse_embeddings_dict[feat_name] = self.embedding_dict[feat_name](sparse_idx - 1)

        # N, k, 10
        # (bs num_field*10)
        lin_embedding = torch.cat(list(sparse_embeddings_dict.values()), dim=-1)
        lin_logits = (lin_embedding @ self.trans_weight)
        dense_values_list = list(dense_features.values())
        dense_dnn_input = torch.stack(dense_values_list, dim=-1).float()
        # print('dense_dnn_input.type:',dense_dnn_input.type())
        dense_logits = (dense_dnn_input @ self.weight)
        # f = w1*离散变量+ w2*连续变量
        return lin_logits + dense_logits


class CIN(nn.Module):
    """Compressed Interaction Network used in xDeepFM.
      Input shape
        - 3D tensor with shape: ``(batch_size,field_size,embedding_size)``.
      Output shape
        - 2D tensor with shape: ``(batch_size, featuremap_num)``
        ``featuremap_num =  sum(self.layer_size[:-1]) // 2 + self.layer_size[-1]``
        if ``split_half=True``,else  ``sum(layer_size)`` .
      Arguments
        - **filed_size** : Positive integer, number of feature groups.
        - **layer_size** : list of int.Feature maps in each layer.
        - **activation** : activation function name used on feature maps.
        - **split_half** : bool.if set to False, half of the feature maps in each hidden will connect to output unit.
        - **seed** : A Python integer to use as random seed.
      References
        - [Lian J, Zhou X, Zhang F, et al. xDeepFM: Combining Explicit and Implicit Feature Interactions for
        Recommender Systems[J]. arXiv preprint arXiv:1803.05170, 2018.] (https://arxiv.org/pdf/1803.05170.pdf)
    """

    def __init__(self, field_size, layer_size=(128, 128), activation='relu', split_half=True, l2_reg=1e-5, seed=1024,
                 device='cpu'):
        super(CIN, self).__init__()
        if len(layer_size) == 0:
            raise ValueError(
                "layer_size must be a list(tuple) of length greater than 1")

        self.layer_size = layer_size
        self.field_nums = [field_size]
        self.split_half = split_half
        self.activation = activation_layer(activation)
        self.l2_reg = l2_reg
        self.seed = seed

        self.conv1ds = nn.ModuleList()
        for i, size in enumerate(self.layer_size):
            self.conv1ds.append(
                nn.Conv1d(self.field_nums[-1] * self.field_nums[0], size, 1))

            if self.split_half:
                if i != len(self.layer_size) - 1 and size % 2 > 0:
                    raise ValueError(
                        "layer_size must be even number except for the last layer when split_half=True")

                self.field_nums.append(size // 2)
            else:
                self.field_nums.append(size)

        #         for tensor in self.conv1ds:
        #             nn.init.normal_(tensor.weight, mean=0, std=init_std)
        self.to(device)

    def forward(self, inputs):
        if len(inputs.shape) != 3:
            raise ValueError(
                "Unexpected inputs dimensions %d, expect to be 3 dimensions" % (len(inputs.shape)))
        batch_size = inputs.shape[0]  # 16
        dim = inputs.shape[-1]  # 10
        hidden_nn_layers = [inputs]
        final_result = []

        for i, size in enumerate(self.layer_size):
            # x^(k-1) * x^0
            x = torch.einsum(
                'bhd,bmd->bhmd', hidden_nn_layers[-1], hidden_nn_layers[0])
            # x.shape = (batch_size , hi * m, dim)
            x = x.reshape(
                batch_size, hidden_nn_layers[-1].shape[1] * hidden_nn_layers[0].shape[1], dim)
            # x.shape = (batch_size , hi, dim)
            x = self.conv1ds[i](x)

            if self.activation is None or self.activation == 'linear':
                curr_out = x
            else:
                curr_out = self.activation(x)

            if self.split_half:
                if i != len(self.layer_size) - 1:
                    next_hidden, direct_connect = torch.split(
                        curr_out, 2 * [size // 2], 1)
                else:
                    direct_connect = curr_out
                    next_hidden = 0
            else:
                direct_connect = curr_out
                next_hidden = curr_out

            final_result.append(direct_connect)
            hidden_nn_layers.append(next_hidden)

        result = torch.cat(final_result, dim=1)
        result = torch.sum(result, -1)

        return result


class Expert(nn.Module):

    def __init__(self, config: Namespace):
        super(Expert, self).__init__()
        self.config = config

        self.embedding_dict = create_embedding_dict(config)
        # self.fm = FM()
        self.cin = CIN(field_size=config.num_field,
                       layer_size=config.cin_layer_size,
                       activation=config.cin_activation,
                       split_half=config.cin_split_half,
                       l2_reg=config.l2_reg_cin,
                       seed=config.seed,
                       device=config.device)
        if config.cin_split_half:
            self.num_feature_map = sum(config.cin_layer_size[:-1]) // 2 + config.cin_layer_size[-1]
        else:
            self.num_feature_map = sum(config.cin_layer_size)
        self.dense_bn = nn.BatchNorm1d(config.dnn_inputs_dim)
        self.dnn = DNN(inputs_dim=config.dnn_inputs_dim,
                       hidden_units=config.dnn_hidden_units,
                       activation=config.dnn_activation,
                       l2_reg=config.l2_reg_dnn,
                       dropout_rate=config.dnn_dropout,
                       use_bn=config.dnn_use_bn,
                       init_std=config.init_std,
                       seed=config.seed,
                       device=config.device)

        self.attent_layer = nn.Sequential(nn.BatchNorm1d(256 + 128),
                                          nn.Linear(256 + 128, 32),
                                          nn.BatchNorm1d(32),
                                          nn.ReLU(),
                                          nn.Linear(32, 32),
                                          nn.BatchNorm1d(32),
                                          nn.ReLU(),
                                          nn.Linear(32, 256 + 128),
                                          nn.Sigmoid())

    def forward(
            self,
            dense_features: torch.Tensor,
            sparse_features: Dict[str, torch.Tensor],
    ):
        """
        :param dense_features: (bs, num_dense(1-feed时长))
        :param sparse_features: e.g. {'userid': (bs, )}

        :return:
        """
        sparse_embeddings_dict = defaultdict(list)

        for feat_name, sparse_idx in sparse_features.items():
            if feat_name in ['gender', 'search_token']:
                # 性别是从0开始，其他类别变量都是从1开始，对应embedding中的索引要-1
                sparse_embeddings_dict[feat_name] = self.embedding_dict[feat_name](sparse_idx)
            else:
                sparse_embeddings_dict[feat_name] = self.embedding_dict[feat_name](sparse_idx - 1)

        sparse_embeddings_list = list(sparse_embeddings_dict.values())

        # 稀疏特征的组合
        # 16,64
        # num_field (bs,emb_size) -> (bs, num_field, emb_size)
        cin_input = torch.stack(sparse_embeddings_list, dim=-1).permute(0, 2, 1)  # (bs, num_field, emb_size)
        cin_feat = self.cin(cin_input)

        dense_values_list = list(dense_features.values())
        sparse_dnn_input = torch.flatten(torch.cat(sparse_embeddings_list, dim=-1), start_dim=1)
        dense_dnn_input = torch.stack(dense_values_list, dim=-1)
        # print('dense_values_list:',dense_values_list)
        dnn_input = torch.cat([sparse_dnn_input, dense_dnn_input], dim=1)
        dense_inputs = self.dense_bn(dnn_input)
        #
        dnn_feat = self.dnn(dense_inputs)
        feats = torch.cat([cin_feat, dnn_feat], 1)
        # feats = feats * self.attent_layer(feats)
        feats = self.attent_layer(feats)  # need vrify.
        # print('feats:',feats)
        return feats


class TaskTower(nn.Module):
    def __init__(self, in_chans):
        super(TaskTower, self).__init__()
        self.dnn_logits = nn.Sequential(
            nn.BatchNorm1d(in_chans),
            nn.Linear(in_chans, 128),
            nn.GELU(),
            nn.Linear(128, 1))

    def forward(self, dnn_feat):
        dnn_logits = self.dnn_logits(dnn_feat)
        return dnn_logits


class MultiDeepFM(nn.Module):

    def __init__(self, config: Namespace):
        super(MultiDeepFM, self).__init__()
        self.config = config
        self.num_expert = 3
        self.task_num = 3
        self.embedding_dict = create_embedding_dict(config)
        # feed embedding and dnn fuse 256 + 128
        self.feed_bn = nn.BatchNorm1d(config.dnn_hidden_units[-1] + 256)
        self.feed_fc = nn.Sequential(
            nn.Linear(config.dnn_hidden_units[-1] + 256, 256),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, self.task_num)
        )
        # self.long_short_mem = LongShortMem(config)
        self.lin = Linear(config)
        self.expert_list = nn.ModuleList([Expert(self.config) for i in range(self.num_expert)])
        self.input_size = self.config.dnn_inputs_dim
        self.gates_linear = nn.ModuleList(
            [nn.Linear(self.input_size, self.num_expert) for i in range(self.task_num)])
        self.in_chans = self.config.dnn_hidden_units[-1] + self.config.cin_layer_size[-1] * 2
        self.tower_list = nn.ModuleList([TaskTower(self.in_chans) for i in range(self.task_num)])

        self.loss_fct = FocalLoss_MultiLabel(config=config)  # nn.BCEWithLogitsLoss(reduction='none') #

    def forward(
            self,
            dense_features: torch.Tensor,
            sparse_features: Dict[str, torch.Tensor],
            labels: torch.Tensor = None
    ):
        sparse_embeddings_dict = defaultdict(list)

        for feat_name, sparse_idx in sparse_features.items():
            if feat_name in ['gender', 'search_token']:
                # 性别和search_token2id是从0开始，其他类别变量都是从1开始，对应embedding中的索引要-1
                sparse_embeddings_dict[feat_name] = self.embedding_dict[feat_name](sparse_idx)
            else:

                sparse_embeddings_dict[feat_name] = self.embedding_dict[feat_name](sparse_idx - 1)

        # 多个key，sum
        # shape:4,5,10    4个特征，bs = 5,embedding 10
        sparse_embeddings_list = list(sparse_embeddings_dict.values())

        # (bs, 200)       (1,bs)
        dense_values_list = list(dense_features.values())

        sparse_gate_input = torch.flatten(torch.cat(sparse_embeddings_list, dim=-1), start_dim=1)
        dense_gate_input = torch.stack(dense_values_list, dim=-1)
        gate_inputs = torch.cat([sparse_gate_input, dense_gate_input], dim=1)
        self.expert_feat = []
        for layer in self.expert_list:
            # layer是deepfm层
            self.expert_feat.append(layer(dense_features, sparse_features,
                                          ))

        self.expert_feat = torch.stack(self.expert_feat, 1)

        task_logits = []
        for i in range(self.task_num):
            attent = self.gates_linear[i](gate_inputs)
            attent = F.softmax(attent, dim=-1).unsqueeze(-1)
            task_input = (attent * self.expert_feat).sum(1)
            task_logits.append(self.tower_list[i](task_input))

        labels = torch.stack(list(labels.values()), dim=1)
        deep_logits = torch.cat(task_logits, 1)
        lin_logits = self.lin(dense_features, sparse_features)
        logits = lin_logits + deep_logits
        loss = self.loss_fct(logits, labels)
        pos_loss = loss[labels == 1].sum()
        neg_loss = loss[labels == 0].sum()
        loss = loss.sum()
        return pos_loss, neg_loss, loss, logits, labels
