# -*- coding: utf-8 -*-
# @Time    : 2022/5/9 2:27 下午
# @Author  : zhengjiawei
# @FileName: test.py
# @Software: PyCharm
import os

import horovod.torch as hvd
import torch
from ranker.src.args import get_args
from ranker.src.dataloader import load_data
from ranker.src.model import MultiDeepFM
from ranker.src.utils import batch2cuda, EMA, seed_everything, roc_score
from torch.optim import Adagrad
from tqdm import tqdm, trange


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
        t = time.time()
        for batch in test_iterator:
            batch_cuda, _ = batch2cuda(batch, config)
            logits = model(**batch_cuda)[3]
            probs = torch.sigmoid(logits)
            test_preds.append(probs.detach().cpu())

    ts = (time.time() - t) * 1000.0 / len(test_df) * 2000.0
    print(f'\n>>> Single action average cost time {ts:.4} ms on 2000 samples ...')

    test_preds = torch.cat(test_preds).numpy()
    return test_preds


def main():
    args = args_setup()
    process_valid_data = ReadData(train=False)
    test_dataset = SearchDataset(process_valid_data)
    # test_sampler = torch.utils.data.distributed.DistributedSampler(
    #     test_dataset, num_replicas=hvd.size(), rank=hvd.rank())

    test_dataloader = DataLoader(dataset=test_dataset, batch_size=args.bs,
                                 num_workers=4, pin_memory=False,
                                 shuffle=False)
    model = MultiDeepFM(args)
    model.to(args.device)
    args.best_model_path = os.path.join(args.output_dir, 'best.pth')
    model.load_state_dict(torch.load(args.best_model_path))

    predict(args, model, test_dataloader)


if __name__ == '__main__':
    main()
