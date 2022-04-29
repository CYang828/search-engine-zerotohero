# -*- coding: utf-8 -*-
# @Time    : 2022/2/23 8:54 下午
# @Author  : zhengjiawei
# @FileName: bert_pretrain.py
# @Software: PyCharm

import os
import random
from collections import defaultdict
from typing import Tuple, List

import numpy as np
import torch
from torch.utils.data import Dataset
from tqdm import tqdm
from transformers import BertTokenizer, BertForMaskedLM, Trainer, TrainingArguments

from public.bert_wwm_pretrain.processing import check_dir

# Create an experiment with your api key
# 为了记录数据，这是我自己的comet账号
# experiment = Experiment(
#     api_key="I1gv6gvPEQfgfHauwuDYCEpqV",
#     project_name="search-engine-zerotohero",
#     workspace="zhengjiawei",
# )
os.environ['CUDA_VISIBLE_DEVICES'] = '2'


class SearchDataset(Dataset):
    def __init__(self, data_dict: dict):
        self.data_dict = data_dict

    def __getitem__(self, index: int) -> tuple:
        data = (self.data_dict['input_ids'][index], self.data_dict['token_type_ids'][index],
                self.data_dict['attention_mask'][index])
        return data

    def __len__(self) -> int:
        return len(self.data_dict['input_ids'])


class SearchCollator:
    def __init__(self, max_seq_len: int, tokenizer: BertTokenizer, mlm_probability=0.15):
        # max_seq_len 用于截断的最大长度
        self.max_seq_len = max_seq_len
        self.tokenizer = tokenizer
        self.mlm_probability = mlm_probability

    def truncate_and_pad(self, input_ids_list, token_type_ids_list,
                         attention_mask_list, max_seq_len):
        input_ids = torch.zeros((len(input_ids_list), max_seq_len), dtype=torch.long)
        token_type_ids = torch.zeros_like(input_ids)
        attention_mask = torch.zeros_like(input_ids)
        for i in range(len(input_ids_list)):
            seq_len = min(len(input_ids_list[i]), max_seq_len)
            if seq_len <= max_seq_len:
                input_ids[i, :seq_len] = torch.tensor(input_ids_list[i][:seq_len], dtype=torch.long)
            else:
                input_ids[i, :seq_len] = torch.tensor(input_ids_list[i][:seq_len - 1] +
                                                      [self.tokenizer.sep_token_id], dtype=torch.long)
            token_type_ids[i, :seq_len] = torch.tensor(token_type_ids_list[i][:seq_len], dtype=torch.long)
            attention_mask[i, :seq_len] = torch.tensor(attention_mask_list[i][:seq_len], dtype=torch.long)
        return input_ids, token_type_ids, attention_mask

    def _whole_word_mask(self, input_ids_list: List[str], max_seq_len: int, max_predictions=512):
        cand_indexes = []
        for (i, token) in enumerate(input_ids_list):
            if (token == str(self.tokenizer.cls_token_id)
                    or token == str(self.tokenizer.sep_token_id)):
                continue

            if len(cand_indexes) >= 1 and token.startswith("##"):
                cand_indexes[-1].append(i)
            else:
                cand_indexes.append([i])

        random.shuffle(cand_indexes)
        num_to_predict = min(max_predictions, max(1, int(round(len(input_ids_list) * self.mlm_probability))))
        masked_lms = []
        covered_indexes = set()
        for index_set in cand_indexes:
            if len(masked_lms) >= num_to_predict:
                break
            if len(masked_lms) + len(index_set) > num_to_predict:
                continue
            is_any_index_covered = False
            for index in index_set:
                if index in covered_indexes:
                    is_any_index_covered = True
                    break
            if is_any_index_covered:
                continue
            for index in index_set:
                covered_indexes.add(index)
                masked_lms.append(index)

        assert len(covered_indexes) == len(masked_lms)
        mask_labels = [1 if i in covered_indexes else 0 for i in range(min(len(input_ids_list), max_seq_len))]

        mask_labels += [0] * (max_seq_len - len(mask_labels))
        return torch.tensor(mask_labels)

    def mask_tokens(self, inputs: torch.Tensor, mask_labels: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:

        labels = inputs.clone()

        probability_matrix = mask_labels

        special_tokens_mask = [
            self.tokenizer.get_special_tokens_mask(val, already_has_special_tokens=True) for val in labels.tolist()
        ]
        probability_matrix.masked_fill_(torch.tensor(special_tokens_mask, dtype=torch.bool), value=0.0)
        if self.tokenizer.pad_token is not None:
            padding_mask = labels.eq(self.tokenizer.pad_token_id)
            probability_matrix.masked_fill_(padding_mask, value=0.0)

        masked_indices = probability_matrix.bool()
        labels[~masked_indices] = -100

        indices_replaced = torch.bernoulli(torch.full(labels.shape, 0.8)).bool() & masked_indices
        inputs[indices_replaced] = self.tokenizer.convert_tokens_to_ids(self.tokenizer.mask_token)

        indices_random = torch.bernoulli(torch.full(labels.shape, 0.5)).bool() & masked_indices & ~indices_replaced
        random_words = torch.randint(len(self.tokenizer), labels.shape, dtype=torch.long)
        inputs[indices_random] = random_words[indices_random]

        return inputs, labels

    def whole_word_mask(self, input_ids_list: List[list], max_seq_len: int) -> torch.Tensor:
        mask_labels = []
        for input_ids in input_ids_list:
            wwm_id = random.choices(range(len(input_ids)), k=int(len(input_ids) * 0.2))

            input_id_str = [f'##{id_}' if i in wwm_id else str(id_) for i, id_ in enumerate(input_ids)]
            mask_label = self._whole_word_mask(input_id_str, max_seq_len)
            mask_labels.append(mask_label)
        return torch.stack(mask_labels, dim=0)

    def __call__(self, examples: list) -> dict:
        input_ids_list, token_type_ids_list, attention_mask_list = list(zip(*examples))
        cur_max_seq_len = max(len(input_id) for input_id in input_ids_list)
        # 动态识别 batch 中最大长度，用于 padding 操作
        max_seq_len = min(cur_max_seq_len, self.max_seq_len)

        input_ids, token_type_ids, attention_mask = self.truncate_and_pad(input_ids_list,
                                                                          token_type_ids_list,
                                                                          attention_mask_list,
                                                                          max_seq_len)
        batch_mask = self.whole_word_mask(input_ids, max_seq_len)
        input_ids, mlm_labels = self.mask_tokens(input_ids, batch_mask)
        data_dict = {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'token_type_ids': token_type_ids,
            'labels': mlm_labels
        }

        return data_dict


def read_data(train_file_path, tokenizer: BertTokenizer, debug=False) -> dict:
    train_data = open(train_file_path, 'r', encoding='utf8').readlines()
    if debug:
        train_data = train_data[:2000]

    inputs = defaultdict(list)
    for row in tqdm(train_data, desc=f'Preprocessing train data', total=len(train_data)):
        sentence = row.strip()
        inputs_dict = tokenizer.encode_plus(sentence, add_special_tokens=True,
                                            return_token_type_ids=True, return_attention_mask=True)
        inputs['input_ids'].append(inputs_dict['input_ids'])
        inputs['token_type_ids'].append(inputs_dict['token_type_ids'])
        inputs['attention_mask'].append(inputs_dict['attention_mask'])

    return inputs


def seed_everyone(seed_):
    torch.manual_seed(seed_)
    torch.cuda.manual_seed_all(seed_)
    np.random.seed(seed_)
    random.seed(seed_)
    return seed_


class CFG:
    corpus_file_path = 'public/bert_wwm_pretrain/data/pretrain_corpus.txt'
    vocab_file_path = 'public/bert_wwm_pretrain/data/chinese_bert_wwm/vocab.txt'
    redis_url = "10.30.89.124"
    redis_port = 6379
    max_seq_len = 102
    batch_size = 32
    output_dir = 'public/bert_wwm_pretrain/data/whole_word_mask_bert_output'
    bert_model_dir = 'public/bert_wwm_pretrain/data/chinese_bert_wwm/'
    debug = False


def main():
    seed_everyone(20210318)
    # experiment.log_parameters(CFG)
    train_file_path = CFG.corpus_file_path
    tokenizer = BertTokenizer.from_pretrained(CFG.vocab_file_path, local_files_only=True)
    data = read_data(train_file_path, tokenizer, CFG.debug)
    train_dataset = SearchDataset(data)
    data_collator = SearchCollator(max_seq_len=CFG.max_seq_len, tokenizer=tokenizer, mlm_probability=0.15)

    output_dir = CFG.output_dir
    model = BertForMaskedLM.from_pretrained(CFG.bert_model_dir)

    model_save_dir = os.path.join(output_dir, 'best_model_ckpt')
    tokenizer_and_config = os.path.join(output_dir, 'tokenizer_and_config')
    check_dir(model_save_dir)
    check_dir(tokenizer_and_config)
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=20,
        fp16_backend='auto',
        per_device_train_batch_size=128,
        save_steps=500,
        logging_steps=500,
        save_total_limit=5,
        prediction_loss_only=True,
        # report_to='comet_ml',
        logging_first_step=True,
        dataloader_num_workers=4,
        disable_tqdm=False,
        seed=202203
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )

    trainer.train()
    trainer.save_model(model_save_dir)
    # config.save_pretrained(tokenizer_and_config)
    tokenizer.save_pretrained(tokenizer_and_config)


if __name__ == "__main__":
    main()

    # length = []
    # for each in data['input_ids']:
    #     length.append(len(each))
    # np.percentile(length, 95) # 102
