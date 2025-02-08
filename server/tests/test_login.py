import requests

URL = "https://vis.pku.edu.cn/prompthis"

response = requests.post(url=f'{URL}/login', json={ 'username': 'root'})
print(response.json())
