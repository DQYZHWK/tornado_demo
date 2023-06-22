import requests

url = 'http://localhost:20001/api'
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print('请求失败：', response.status_code)
