# -*- coding: utf-8 -*-
# @Time    : 2022/4/7 8:04 下午
# @Author  : zhengjiawei
# @FileName: args.py
# @Software: PyCharm
import argparse
import os


def get_args():
    parser = argparse.ArgumentParser(description='XDeepFM')

    parser.add_argument('--seed', type=int, default=12)
    parser.add_argument('--device', type=str, default='cuda:3')
    ########################## XDeepFM ##########################
    parser.add_argument('--multi_modal_hidden_size', type=int, default=128)
    parser.add_argument('--num_field', type=int, default=6)
    parser.add_argument('--cin_layer_size', type=tuple, default=(256, 128))
    parser.add_argument('--cin_split_half', type=bool, default=True)
    parser.add_argument('--cin_activation', type=str, default='relu')
    parser.add_argument('--dnn_activation', type=str, default='relu')
    parser.add_argument('--l2_reg_cin', type=float, default=0.)
    parser.add_argument('--l2_reg_dnn', type=float, default=0.)
    parser.add_argument('--dnn_use_bn', type=bool, default=True)
    parser.add_argument('--init_std', type=float, default=0.0001)
    parser.add_argument('--dnn_dropout', type=float, default=0.)
    parser.add_argument('--dnn_hidden_units', type=tuple, default=(256, 128, 128))
    parser.add_argument('--dnn_inputs_dim', type=int, default=62)
    parser.add_argument('--l2_reg_embedding', type=float, default=1e-5)
    parser.add_argument('--l2_reg_linear', type=float, default=1e-5)
    parser.add_argument('--l2', type=float, default=1e-3)
    ########################## XDeepFM ##########################

    parser.add_argument('--sparse_feature_info', type=list,
                        default=[('userid', 100000, 10), ('gender', 2, 10),
                                 ('city', 36, 10),('age', 4, 10),
                                 ('job', 12, 10), ('education', 5, 10),
                                 ('search_token', 598040, 10)  # 共有598039个token
                                 ])

    parser.add_argument('--num_folds', type=int, default=20)
    parser.add_argument('--num_epochs', type=int, default=2)
    parser.add_argument('--lr', type=float, default=0.01)
    parser.add_argument('--bs', type=int, default=16)
    parser.add_argument('--output_dir', type=str, default="")
    parser.add_argument('--ema_start', type=bool, default=False)
    parser.add_argument('--logging_steps', type=int, default=500)
    parser.add_argument('--ema_start_step', type=int, default=40)
    parser.add_argument('--bucket_size_multiplier', type=int, default=10)
    parser.add_argument('--best_model_path', type=str, default='')
    parser.add_argument('--debug_data', action='store_true')

    args = parser.parse_args()
    args.output_dir = os.path.join('ranker/src', "nn_" + str(args.seed))
    return args
