# -*- coding: utf-8 -*-
# @Time    : 2022/4/7 5:35 下午
# @Author  : zhengjiawei
# @FileName: train.py
# @Software: PyCharm
import os

import horovod.torch as hvd
import torch
from torch.optim import Adagrad
from tqdm import tqdm, trange

from ranker.src.args import get_args
from ranker.src.dataloader import load_data
from ranker.src.model import MultiDeepFM
from ranker.src.utils import batch2cuda, EMA, seed_everything, roc_score


def evaluation(config, model, val_dataloader):
    model.eval()
    preds = []
    labels = []
    val_loss = 0.
    val_iterator = tqdm(val_dataloader, desc='Evaluation', total=len(val_dataloader))
    user_ids = []
    with torch.no_grad():
        for batch in val_iterator:
            user_id = list(batch[0])
            sparse_features = batch[1]
            dense_features = batch[2]
            label = batch[3]
            user_ids.extend(user_id)
            sparse_features = batch2cuda(sparse_features, config)
            dense_features = batch2cuda(dense_features, config)
            label = batch2cuda(label, config)
            pos_loss, neg_loss, loss, logits, label = model(dense_features, sparse_features, label)
            labels.append(label.detach().cpu())
            #             nums_preds = (torch.sigmoid(nums_logits) > 0.5).int()
            #             nums_pred_list.append(nums_preds.detach().cpu())
            probs = torch.sigmoid(logits)

            loss /= len(user_ids)
            if config.n_gpus > 1:
                loss = loss.mean()

            val_loss += loss.item()
            preds.append(probs.detach().cpu())
    total_labels = torch.cat(labels, 0)
    avg_val_loss = val_loss / len(val_dataloader)
    metrics = roc_score(labels, preds, user_ids)
    metrics['val_loss'] = avg_val_loss
    return metrics


def evaluation_and_save(best_model_path, best_roc_auc, config, global_steps, model,
                        print_train_loss, print_pos_loss, print_neg_loss, print_num_loss, valid_dataloader):
    metrics = evaluation(config, model, valid_dataloader)
    roc_auc = metrics['avg_roc']
    print_log = f'\n>>> training loss: {print_train_loss:.4f} '
    if roc_auc > best_roc_auc:
        model_save_path = f'{config.output_dir}/best.pth'
        model_to_save = model.module if hasattr(model, 'module') else model
        torch.save(model_to_save.state_dict(), model_save_path)
        best_roc_auc = roc_auc
        best_model_path = model_save_path
    for metric, score in metrics.items():
        print_log += f'{metric}: {score:.4f} '
    print(print_log)
    metrics[f'train_loss'] = print_train_loss
    metrics[f'pos_loss'] = print_pos_loss
    metrics[f'neg_loss'] = print_neg_loss
    metrics[f'num_loss'] = print_num_loss
    return best_model_path, best_roc_auc


def train(config, train_dataloader, valid_dataloader):
    model = MultiDeepFM(config)
    model.to(config.device)
    optimizer = Adagrad(model.parameters(), lr=config.lr)

    hvd.broadcast_parameters(model.state_dict(), root_rank=0)
    hvd.broadcast_optimizer_state(optimizer, root_rank=0)
    # compression = hvd.Compression.fp16 if config.fp16_allreduce else hvd.Compression.none
    optimizer = hvd.DistributedOptimizer(optimizer, named_parameters=model.named_parameters())

    epoch_iterator = trange(config.num_epochs, desc='Epoch')
    global_steps = 0
    train_loss = 0.
    pos_train_loss = 0.
    train_num_loss = 0.
    neg_train_loss = 0.
    logging_loss = 0.
    best_roc_auc = 0.
    best_model_path = ''

    # if config.n_gpus > 1:
    #     model = torch.nn.DataParallel(model)

    optimizer.zero_grad()

    for _ in epoch_iterator:

        train_iterator = tqdm(train_dataloader, desc='Training', total=len(train_dataloader))
        model.train()
        for batch in train_iterator:
            user_ids = list(batch[0])
            sparse_features = batch[1]
            dense_features = batch[2]
            labels = batch[3]
            sparse_features = batch2cuda(sparse_features, config)
            dense_features = batch2cuda(dense_features, config)
            labels = batch2cuda(labels, config)
            total_reg_loss = 0.
            # 需要传入 dense_features,sparse_features,labels
            pos_loss, neg_loss, loss = model(dense_features, sparse_features, labels)[:3]
            for n, p in model.named_parameters():
                if "weight" in n:
                    if "embedding" in n:
                        total_reg_loss += torch.sum(config.l2_reg_embedding * torch.square(p))
                    else:
                        total_reg_loss += torch.sum(config.l2 * torch.square(p))
            # if config.n_gpus > 1:
            #     loss = loss.mean()
            #     pos_loss = pos_loss.mean()
            #     neg_loss = neg_loss.mean()
            loss += total_reg_loss
            loss /= len(user_ids)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            # scheduler.step()
            optimizer.zero_grad()

            if config.ema_start:
                ema.update()

            train_loss += loss.item()
            pos_train_loss += pos_loss.item()
            neg_train_loss += neg_loss.item()
            #             train_num_loss += nums_loss.item()
            global_steps += 1

            train_iterator.set_postfix_str(f'running training loss: {loss.item():.4f}')
            # EXPERIMENT.log_metric(f'running {config.action} training loss', loss.item(), step=global_steps)
            if global_steps % config.logging_steps == 0:
                if global_steps >= config.ema_start_step and not config.ema_start:
                    print('\n>>> EMA starting ...')
                    config.ema_start = True
                    ema = EMA(model.module if hasattr(model, 'module') else model, decay=0.999)

                print_train_loss = (train_loss - logging_loss) / config.logging_steps
                print_pos_loss = pos_train_loss / config.logging_steps
                print_neg_loss = neg_train_loss / config.logging_steps
                print_num_loss = train_num_loss / config.logging_steps
                logging_loss = train_loss
                pos_train_loss = 0.
                neg_train_loss = 0.
                train_num_loss = 0.
                if config.ema_start:
                    ema.apply_shadow()
                best_model_path, best_roc_auc = evaluation_and_save(best_model_path, best_roc_auc, config,
                                                                    global_steps, model,
                                                                    print_train_loss, print_pos_loss, print_neg_loss,
                                                                    print_num_loss, valid_dataloader)
                model.train()
                if config.ema_start:
                    ema.restore()

    if global_steps % config.logging_steps != 0:
        print_train_loss = (train_loss - logging_loss) / (global_steps % config.logging_steps)
        print_pos_loss = pos_train_loss / (global_steps % config.logging_steps)
        print_neg_loss = neg_train_loss / (global_steps % config.logging_steps)
        print_num_loss = train_num_loss / (global_steps % config.logging_steps)
        print('train_loss:', print_train_loss)
        print('pos_loss:', print_pos_loss)
        print('neg_loss:', print_neg_loss)
        print('num_loss:', print_num_loss)

    return model, best_model_path


def args_setup():
    args = get_args()
    seed_everything(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)
    if not torch.cuda.is_available():
        args.device = 'cpu'
    # else:
    #     # args.n_gpus = torch.cuda.device_count()
    #     # args.bs *= args.n_gpus
    #     # args.device = 'cpu'
    #     args.n_gpus = 1
    return args


if __name__ == '__main__':
    hvd.init()
    torch.cuda.set_device(hvd.local_rank())
    args = args_setup()
    print('start training')
    train_dataloader, valid_dataloader = load_data(args)
    train(args, train_dataloader, valid_dataloader)
