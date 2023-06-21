# coding: UTF-8
import time
import torch
import numpy as np
from train_eval import train, init_network,only_test
from importlib import import_module
import argparse
import logging
from utils import build_dataset, build_iterator, get_time_dif

parser = argparse.ArgumentParser(description='Chinese Text Classification')
parser.add_argument('--model', type=str, required=True, help='choose a model: Bert, ERNIE')
parser.add_argument('--test', type=str, required=True)
args = parser.parse_args()


#所以，if__name__== '__main__'的意思是：当py文件被直接运行时，if__name__=='__main__'之下的代码将被运行；
# 当py文件以模块形式被导入时，if __name__=='__main__'之下的代码块不被运行。
if __name__ == '__main__':

    dataset = 'THUCNews'  # 数据集

    model_name = args.model  # bert
    x = import_module('models.' + model_name) #动态导入函数
    config = x.Config(dataset) # 初始化模型并装入数据
    np.random.seed(1) 
    torch.manual_seed(1)
    torch.cuda.manual_seed_all(1)
    torch.backends.cudnn.deterministic = True  # 保证每次结果一样

    start_time = time.time()
    print("Loading data...")
    # 预处理后：

    train_data, dev_data, test_data = build_dataset(config)
    #print('after tokenize of data',end='')
    print(train_data[0])
    train_iter = build_iterator(train_data, config)
    dev_iter = build_iterator(dev_data, config)

    test_iter = build_iterator(test_data, config)
    time_dif = get_time_dif(start_time)
    print("Time usage:", time_dif)


    # train

    
    model = x.Model(config).to(config.device)
    if args.test == "no":
        train(config, model, train_iter, dev_iter, test_iter)
    else:
        only_test(config,model,test_iter)
    """
    1.把原始中文数据通过bert模型实现token化（实现了中文得分词？）,然后得到对应在词表中得位置
    BERT格式（token_ids，seq_len，mask）
    
    Bert重得Tokenizer得说明（https://blog.csdn.net/weixin_42223207/article/details/119336324）


    2.BERT模型在文本前插入一个[CLS]符号，并将该符号对应的输出向量作为整篇文本的语义表示，用于文本分类.
    (语句对分类任务：需要添加[SEP]，比如立场分析，QA问题)
    3.??????Batch Normalization   and  Dropout   and no decay?(reveiw)
    pytorch中的model. train()和model. eval()到底做了什么？(https://www.zhihu.com/question/429337764/answer/2596651002)
    
    """
