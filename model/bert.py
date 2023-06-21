# coding: UTF-8
import torch
import torch.nn as nn
# from pytorch_pretrained_bert import BertModel, BertTokenizer
from pytorch_pretrained import BertModel, BertTokenizer


class Config(object):

    """配置参数"""
    def __init__(self, dataset):
        self.model_name = 'bert'
        self.train_path = dataset + '/data/train.csv'                                # 训练集
        self.dev_path = dataset + '/data/dev.csv'                                    # 验证集
        self.test_path = dataset + '/data/test.csv'                                  # 测试集
        self.class_list = [x.strip('\n') for x in open(
            dataset + '/data/class2.txt').readlines()]                                # 类别名单
        self.save_path = dataset + '/saved_dict2/' + self.model_name + '.ckpt'        # 模型训练结果
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')   # 设备

        self.require_improvement = 1000                                 # 若超过1000batch效果还没提升，则提前结束训练
        self.num_classes = len(self.class_list)                         # 类别.数
        self.num_epochs = 3                                             # epoch数
        self.batch_size = 16                                           # mini-batch大小
        self.pad_size = 512                                             # 每句话处理成的长度(短填长切)
        self.learning_rate = 3e-5                                    # 学习率
        self.bert_path = './bert_pretrain'
        #1
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)  # 需要自己在任务重装载预处理模型得参数
        self.hidden_size = 768


class Model(nn.Module):

    def __init__(self, config):
        super(Model, self).__init__()

        self.bert = BertModel.from_pretrained(config.bert_path)
        for param in self.bert.parameters():
            param.requires_grad = True     # 需要fine-tune
        self.fc = nn.Linear(config.hidden_size, config.num_classes)
        #print(config.num_classes)

    def forward(self, x):
        
        # context 128*32   (1:batch_size 2:lensize（idx of every token）)
        context = x[0]  # 输入的句子
        #print('shape of bert input: ' ,end='')
        
        #print(context.shape)

        mask = x[2]  # 对padding部分进行mask，和句子一个size，padding部分用0表示，如：[1, 1, 1, 1, 0, 0]

        # bert 
        _, pooled = self.bert(context, attention_mask=mask, output_all_encoded_layers=False)
        #print('after of bert : ', end='')
        #print(pooled.shape)
        #print('final layer output : ',end='')
        #print(_.shape)
        out = self.fc(pooled)
        return out
