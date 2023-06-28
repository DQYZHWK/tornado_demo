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
    ioloop.IOLoop.current().start()
