import time
import torch
from concurrent.futures.thread import ThreadPoolExecutor
from importlib import import_module
from medical_cls_model.lstm import Model as lstm
from tornado import gen, web, ioloop
import functools
import json
import jieba
import re
# 初始化病例分类的API工作线程池
executor = ThreadPoolExecutor(max_workers=2)
PAD, CLS = '[PAD]', '[CLS]'
model = lstm().to('cuda' if torch.cuda.is_available() else 'cpu')

# 如果在GPU上部署此模型，去除map_location=torch.device('cpu')
model.load_state_dict(torch.load(model.save_path, map_location=torch.device('cpu')))
model.eval()


# Medical Classification API的处理器类
class MedicalClassificationHandler(web.RequestHandler):
    async def get(self):
        try:
            data = json.loads(self.request.body)
            medical_context = data.get('medical_context')
            processed_sentence = re.sub(r'\s', '', medical_context)
            line_words_row = jieba.cut(processed_sentence)
            line_words = []
            for item in line_words_row:
                if item.isdigit():
                    continue
                line_words.append(item)

            rest = await ioloop.IOLoop.current().run_in_executor(executor, functools.partial(self.process_request,line_words))
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

    def process_request(self, line_words):
        line_words = [model.word2index.get(word, model.word2index['UNK']) for word in line_words]

        if len(line_words) < model.pad_size :
            line_words += ([0] * (model.pad_size-len(line_words)))
        else:
            line_words = line_words[0:model.pad_size]

        line_words = torch.LongTensor(line_words).view(-1, model.pad_size)
        out = model(line_words)
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
