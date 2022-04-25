# -*- coding: utf-8 -*-
# @Time    : 2022/4/7 5:40 下午
# @Author  : zhengjiawei
# @FileName: utils.py
# @Software: PyCharm
import json
import random
from collections import defaultdict

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from numba import njit
from scipy.stats import rankdata


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    return seed


def load_json(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def load_embedding_matrix(filepath='', max_vocab_size=50000):
    embedding_matrix = np.load(filepath)
    flag_matrix = np.zeros_like(embedding_matrix[:2])
    return np.concatenate([flag_matrix, embedding_matrix])[:max_vocab_size]


class EMA:
    def __init__(self, model, decay):
        self.model = model
        self.decay = decay
        self.shadow = {}
        self.backup = {}
        self.register()

    def register(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.shadow[name] = param.data.clone()

    def update(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                new_average = (1.0 - self.decay) * param.data + self.decay * self.shadow[name]
                self.shadow[name] = new_average.clone()

    def apply_shadow(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                self.backup[name] = param.data
                param.data = self.shadow[name]

    def restore(self):
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.backup
                param.data = self.backup[name]
        self.backup = {}


def batch2cuda(batch, config):
    batch_cuda = []
    for k, v in batch.items():
        if isinstance(v, dict):
            v = {vk: vv.to(config.device) for vk, vv in v.items()}
        else:
            v = v.to(config.device)
        batch_cuda.append((k, v))
    batch_cuda = dict(batch_cuda)
    return batch_cuda


def roc_score(labels: list, preds: list,
              user_ids: list) -> dict:
    """多任务学习的 uauc
    read_comment, like, click_avatar, forward
    """
    task2weight = {'click': 1,
                   'like': 2,
                   'comment': 3}

    preds = torch.cat(preds, dim=0).numpy()
    labels = torch.cat(labels, dim=0).numpy()
    columns = [f'{task}_{type_}' for type_ in ['label', 'pred'] for task in task2weight.keys()]
    results_df = pd.DataFrame(data=np.concatenate([labels, preds], axis=-1),
                              columns=columns)
    print('results_df:')
    print(results_df)
    results_df.insert(0, column='user_id', value=user_ids)
    task_metrics = defaultdict(list)
    for _, data in results_df.groupby(by='user_id'):
        for task in task2weight.keys():
            labels = data.loc[:, f'{task}_label'].values
            preds = data.loc[:, f'{task}_pred'].values
            if len(np.unique(labels)) == 1:
                continue
            roc_auc = fast_auc(labels, preds)
            task_metrics[task].append(roc_auc)

    metrics = defaultdict(float)
    avg = 0.
    for task, rocs in task_metrics.items():
        task_roc = sum(rocs) / len(rocs)
        avg += task2weight[task] * task_roc
        metrics[task] = task_roc

    for metric in task2weight.keys():
        if metric not in metrics:
            metrics[metric] = 0.

    avg /= 13
    metrics['avg_roc'] = avg
    return metrics


@njit
def auc(actual, pred_ranks):
    n_pos = np.sum(actual)
    n_neg = len(actual) - n_pos
    return (np.sum(pred_ranks[actual == 1]) - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def fast_auc(actual, predicted):
    # https://www.kaggle.com/c/riiid-test-answer-prediction/discussion/208031
    pred_ranks = rankdata(predicted)
    return auc(actual, pred_ranks)


class FocalLoss(nn.Module):
    def __init__(self, config, alpha=0.25, gamma=2, size_average=True):
        super(FocalLoss, self).__init__()
        self.config = config
        self.alpha = torch.tensor(alpha).to(self.config.device)
        self.gamma = gamma
        self.size_average = size_average

    def forward(self, pred, target):
        # 如果模型最后没有 nn.Sigmoid()，那么这里就需要对预测结果计算一次 Sigmoid 操作
        # pred = nn.Sigmoid()(pred)

        # 展开 pred 和 target,此时 pred.size = target.size = (BatchSize,1)
        pred = pred.view(-1, 1)
        target = target.view(-1, 1)

        # 此处将预测样本为正负的概率都计算出来，此时 pred.size = (BatchSize,2)
        pred = torch.cat((1 - pred, pred), dim=1)

        # 根据 target 生成 mask，即根据 ground truth 选择所需概率
        # 用大白话讲就是：
        # 当标签为 1 时，我们就将模型预测该样本为正类的概率代入公式中进行计算
        # 当标签为 0 时，我们就将模型预测该样本为负类的概率代入公式中进行计算
        class_mask = torch.zeros(pred.shape[0], pred.shape[1]).to(self.config.device)
        # 这里的 scatter_ 操作不常用，其函数原型为:
        # scatter_(dim,index,src)->Tensor
        # Writes all values from the tensor src into self at the indices specified in the index tensor.
        # For each value in src, its output index is specified by its index in src for dimension != dim and by the corresponding value in index for dimension = dim.
        class_mask.scatter_(1, target.view(-1, 1).long(), 1.)

        # 利用 mask 将所需概率值挑选出来
        probs = (pred * class_mask).sum(dim=1).view(-1, 1)
        probs = probs.clamp(min=0.0001, max=1.0)

        # 计算概率的 log 值
        log_p = probs.log()

        # 根据论文中所述，对 alpha　进行设置（该参数用于调整正负样本数量不均衡带来的问题）
        alpha = torch.ones(pred.shape[0], pred.shape[1]).to(self.config.device)
        alpha[:, 0] = alpha[:, 0] * (1 - self.alpha)
        alpha[:, 1] = alpha[:, 1] * self.alpha
        alpha = (alpha * class_mask).sum(dim=1).view(-1, 1)

        # 根据 Focal Loss 的公式计算 Loss
        batch_loss = -alpha * (torch.pow((1 - probs), self.gamma)) * log_p

        # Loss Function的常规操作，mean 与 sum 的区别不大，相当于学习率设置不一样而已
        # if self.size_average:
        #     loss = batch_loss.mean()
        # else:
        #     loss = batch_loss.sum()

        return batch_loss


# 针对 Multi-Label 任务的 Focal Loss
class FocalLoss_MultiLabel(nn.Module):
    def __init__(self, config, alpha=0.25, gamma=2, size_average=True):
        super(FocalLoss_MultiLabel, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.size_average = size_average
        self.config = config

    def forward(self, pred, target):
        criterion = FocalLoss(self.config, self.alpha, self.gamma, self.size_average)
        # loss = torch.zeros(target.size()).to(self.config.device)
        loss = []
        # 对每个 Label 计算一次 Focal Loss
        for label in range(target.shape[1]):
            batch_loss = criterion(pred[:, label], target[:, label])
            # print('loss:', loss)
            # print('batch_loss:', batch_loss)
            loss.append(batch_loss)
        loss = torch.cat(loss, dim=-1)
        # print('loss:', loss)
        # Loss Function的常规操作
        # if self.size_average:
        #     loss = loss.mean()
        # else:
        #     loss = loss.sum()

        return loss
