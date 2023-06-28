# tornado_demo
## 来自一个简单的应用要求
* 首先是完成了支持异步多线程的tornado服务端demo
* 其次是将之前训练好的模型进行封装

---------
2023/6/23 : 发现租的云服务太拉了，尝试在本地测试

---------
2023/6/28 : 尝试直接用词向量表和lstm，200个请求并发从38s到5s


### 接口名称：主诉查体诊疗计划识别
### 接口路径：/api/med_cls
### 请求方式：GET


### 请求参数：
* ctx (string，必填)：病例文书

### 请求示例：
```
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
```


### 响应结果：
   * 成功：
       * 状态码：200
       * 返回数据：json数据，data['data'] = 诊断类别分类

   * 失败：
       * 状态码：4xx
       * 返回数据：
