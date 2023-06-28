'''

# single request

import requests
import json
url = 'http://localhost:20001/api'
params = {'ctx': "出生生长于杭州，未久居外地。否认疫水疫源地接触史，无烟酒等不良嗜好，无不洁性交史；无职业性粉尘、放射性物质、毒物接触史；家庭关系和睦。"}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()  # 将响应的JSON字符串解析为Python对象
    print(data['data'])
   
else:
    print('请求失败：', response.status_code)
'''
# 200个并发的请求

import time
import csv
import threading
import requests
import json

import requests

def call_api(url, params_que):
    headers = {
    'Content-Type': 'application/json',
    'charset': 'UTF-8'
   }
    response = requests.get(url, json=params_que,headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(data['diagnosis_class'])
        print('Response Headers:', response.headers)
        print('Response Body:', response.content.decode('unicode_escape'))
    else:
        print('请求失败：', response.status_code)
# 创建线程列表
threads = []
urls = ['http://localhost:20001/api/medical_classify' for i in range(200)]



f = open("./test.csv", encoding="UTF-8")
freader = csv.reader(f)
params_que = [{'medical_context': row[2][0:-1]} for row in freader]


start_time = time.time()

# 创建并启动线程
for data in zip(urls,params_que):
    t = threading.Thread(target=call_api, args=(data[0], data[1]))
    threads.append(t)
    t.start()

# 等待所有线程执行完成
for t in threads:
    t.join()

print(time.time() - start_time)
print("所有API调用完成")