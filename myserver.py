<<<<<<< HEAD
import time
import torch
from concurrent.futures.thread import ThreadPoolExecutor
from importlib import import_module
from medical_cls_model.only_bert import Model
from tornado import gen, web, ioloop
import functools
import json

# 初始化病例分类的API工作线程池
executor = ThreadPoolExecutor(max_workers=2)
PAD, CLS = '[PAD]', '[CLS]'
model = Model().to('cuda' if torch.cuda.is_available() else 'cpu')

# 如果在GPU上部署此模型，去除map_location=torch.device('cpu')
model.load_state_dict(torch.load(model.save_path, map_location=torch.device('cpu')))
model.eval()

# Medical Classification API的处理器类
class MedicalClassificationHandler(web.RequestHandler):
    async def get(self):
        # 打印请求报文
        print('Request Headers:', self.request.headers)
        print('Request Body:', self.request.body.decode('unicode_escape'))
        
        try:
            data = json.loads(self.request.body)
            medical_context = data.get('medical_context')
            rest = await ioloop.IOLoop.current().run_in_executor(executor, functools.partial(self.process_request, medical_context))
            response = {
                "medical_context": medical_context,
                "diagnosis_class": rest
            }
            self.set_header("Content-Type", "application/json,charset=UTF-8")
            self.write(json.dumps(response))
        
        except Exception as e:
            response = {
                "medical_context": medical_context,
                "error": str(e)
            }
            self.set_header("Content-Type", "application/json;charset=UTF-8")
            self.write(json.dumps(response))

    def process_request(self, medical_context):
        token = model.tokenizer.tokenize(medical_context)
=======

import time
from concurrent.futures.thread import ThreadPoolExecutor
from tornado import gen, web, ioloop
import torch
import numpy as np
from importlib import import_module
from medical_cls_model.only_bert import Model
import functools
import json




# start : inti Medical_Classification  offer model object 
# 病例分类的api的工作线程池
executor = ThreadPoolExecutor(max_workers=2)
PAD, CLS = '[PAD]', '[CLS]'  # padding符号, bert中综合信息符号
model = Model().to(torch.device('cpu'))
model.load_state_dict(torch.load(model.save_path,map_location=torch.device('cpu')))
model.eval()
# end: init Medical_Classificaiton


# start : Medical_Classification api handler
class SyncToAsyncThreadHandler(web.RequestHandler):
    async def get(self, *args, **kwargs):
        rest = await ioloop.IOLoop.current().run_in_executor(executor, functools.partial(self.fun, self))
        response = {
            "data": rest
        }
        response_json = json.dumps(response)
        self.set_header("Content-Type", "application/json")
        self.write(response_json)

    def fun(self,outer):
        start_time = time.time()
        ctx = outer.get_argument('ctx')
        token = model.tokenizer.tokenize(ctx)
>>>>>>> b7c372c5160657fb9f5da096ed282bb36ff87da9
        token = [CLS] + token
        seq_len = len(token)
        mask = []
        token_ids = model.tokenizer.convert_tokens_to_ids(token)
        if len(token) < model.pad_size:
            mask = [1] * len(token_ids) + [0] * (model.pad_size - len(token))
            token_ids += ([0] * (model.pad_size - len(token)))
        else:
            mask = [1] * model.pad_size
            token_ids = token_ids[:model.pad_size]
            seq_len = model.pad_size
        token_ids = torch.LongTensor(token_ids).view(-1, model.pad_size)
<<<<<<< HEAD
        mask = torch.LongTensor(mask).view(-1, model.pad_size)
        seq_len = torch.LongTensor([seq_len])

        out = model((token_ids, seq_len, mask))
        predic = torch.max(out.data, 1)[1].cpu()
        return model.class_list[predic]

if __name__ == '__main__':
    url_map = [
        ("/api/medical_classify", MedicalClassificationHandler)
    ]
    app = web.Application(url_map, debug=True)
    app.listen(20001)
    print('Server started...')
=======
        mask = torch.LongTensor(mask).view(-1,model.pad_size)
        seq_len = torch.LongTensor([seq_len])

        out= model((token_ids, seq_len ,mask))
        predic = torch.max(out.data, 1)[1].cpu()
        get_time = time.time() - start_time
        print(get_time)
        
        return model.class_list[predic]
# end : Medical_Classification api Handler

if __name__ == '__main__':
    url_map = [
        ("/api", SyncToAsyncThreadHandler)
    ]
    app = web.Application(url_map, debug=True)
    app.listen(20001)
    print('started...')
>>>>>>> b7c372c5160657fb9f5da096ed282bb36ff87da9
    ioloop.IOLoop.current().start()
