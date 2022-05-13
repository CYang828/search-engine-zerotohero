# -*- coding: utf-8 -*-
# @Time    : 2022/5/9 2:27 下午
# @Author  : zhengjiawei
# @FileName: test.py
# @Software: PyCharm
import os

# import horovod.torch as hvd
import torch
from ranker.src.args import get_args
from ranker.src.dataloader import load_data, ReadData, SearchDataset
from ranker.src.model import MultiDeepFM
from ranker.src.utils import batch2cuda, EMA, seed_everything, roc_score
from torch.optim import Adagrad
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm, trange
import time

os.environ["CUDA_VISIBLE_DEVICES"] = "3"


def args_setup():
    args = get_args()
    seed_everything(args.seed)
    os.makedirs(args.output_dir, exist_ok=True)
    if not torch.cuda.is_available():
        args.device = 'cpu'
    # else:
    #     args.n_gpus = torch.cuda.device_count()
    #     args.bs *= args.n_gpus
    return args


def predict(config, model, test_dataloader):
    test_iterator = tqdm(test_dataloader, desc='Predicting', total=len(test_dataloader))
    test_preds = []

    model.eval()
    with torch.no_grad():
        for batch in test_iterator:
            sparse_features = batch[1]
            dense_features = batch[2]
            labels = batch[3]
            sparse_features = batch2cuda(sparse_features, config)
            dense_features = batch2cuda(dense_features, config)
            labels = batch2cuda(labels, config)
            logits = model(dense_features, sparse_features, labels)[3]

            probs = torch.sigmoid(logits)
            test_preds.append(probs.detach().cpu())

    test_preds = torch.cat(test_preds).numpy()
    return test_preds


def main():
    args = args_setup()
    process_valid_data = ReadData(train=False, test=True)
    test_dataset = SearchDataset(process_valid_data)

    test_dataloader = DataLoader(dataset=test_dataset, batch_size=args.bs,
                                 num_workers=4, pin_memory=False,
                                 shuffle=False)
    model = MultiDeepFM(args)
    model.to(args.device)
    args.best_model_path = os.path.join(args.output_dir, 'best.pth')
    model.load_state_dict(torch.load(args.best_model_path))

    test_preds = predict(args, model, test_dataloader)
    return test_preds


if __name__ == '__main__':
    test_preds = main()
