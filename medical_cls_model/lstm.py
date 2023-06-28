# coding: UTF-8
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class Model(nn.Module):

    def __init__(self):
        super(Model, self).__init__()
        self.model_name = 'lstm'
        self.class_list = [x.strip() for x in open(
           './medical_cls_model/class.txt',encoding="utf-8").readlines()]                                # 类别名单
        self.save_path = './medical_cls_model/lstmdata/' + self.model_name + '.pth'        # 模型训练结果
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')   # 设备
        self.num_classes = len(self.class_list)                      # 类别数
        self.pad_size = 64                                                                        
        self.hidden_size = 300
        self.dropout = 0.1
        self.rnn_hidden = 300
        self.num_layers = 2   
        
        self.lstm = nn.LSTM(self.hidden_size, self.rnn_hidden, self.num_layers,
                            bidirectional=True, batch_first=True, dropout=self.dropout)
        self.dropout = nn.Dropout(self.dropout)
        self.fc_rnn = nn.Linear(self.rnn_hidden * 2, self.num_classes)
        self.word_embedding = torch.from_numpy(np.load('./medical_cls_model/med_w2v.npz')['embeddings'])

        with open('./medical_cls_model/vocab.words.txt', 'r', encoding='utf-8') as f:
            self.word_vocab = [line.strip() for line in f.readlines()]
        self.word2index = {word: index for index, word in enumerate(self.word_vocab)}

        self.num = 0
    def forward(self, x):
        
        x=self.word_embedding[x].float().to(self.device)
        out, _ = self.lstm(x)
        
        if self.num == 0:
            print("after lstm out",end='')
            print(out.shape)
            
        out = self.dropout(out)
        if self.num == 0:
            print("after dropout out",end='')
            print(out.shape)
        
        out = self.fc_rnn(out[:, -1, :])  # 句子最后时刻的 hidden state

        self.num +=1
        return out
