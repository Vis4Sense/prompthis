import requests

URL = "https://vis.pku.edu.cn/prompthis"

payload = {
    'userId': 0,
}

response = requests.post(url=f'{URL}/fetch/session_list', json=payload)
print(response.json())
