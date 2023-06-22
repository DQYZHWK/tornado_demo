# coding: UTF-8
import torch
import torch.nn as nn
# from pytorch_pretrained_bert import BertModel, BertTokenizer
from pytorch_pretrained import BertModel, BertTokenizer


class Model(nn.Module):

    def __init__(self):
        super(Model, self).__init__()
        
        self.model_name = 'bert'
        self.class_list = [x.strip('\n') for x in open(
           './class.txt',encoding="utf-8").readlines()]                                # 类别名单
        self.save_path = './pad_64/' + self.model_name + '.ckpt'        # 模型训练结果
        self.device = torch.device('cpu')   # 设备
        self.num_classes = len(self.class_list)                         # 类别.数
        self.pad_size = 64                                             # 每句话处理成的长度(短填长切)
        self.bert_path = './bert_pretrain'
        self.tokenizer = BertTokenizer.from_pretrained(self.bert_path)  # 需要自己在任务重装载预处理模型得参数
        self.hidden_size = 768

        self.bert = BertModel.from_pretrained(self.bert_path)

        self.fc = nn.Linear(self.hidden_size, self.num_classes)

    def forward(self, x):
        
        context = x[0]  # 输入的句子

        mask = x[2]  # 对padding部分进行mask，和句子一个size，padding部分用0表示，如：[1, 1, 1, 1, 0, 0]

        # bert 
        _, pooled = self.bert(context, attention_mask=mask, output_all_encoded_layers=False)
        out = self.fc(pooled)
        return out
