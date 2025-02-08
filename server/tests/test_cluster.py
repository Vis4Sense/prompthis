import requests

URL_HOST = 'https://vis.pku.edu.cn/prompthis'

payload = {
    'embeddings': {
        'i1': {'x': 0.1, 'y': 0.1},
        'i2': {'x': 0.2, 'y': 0.2},
        'i3': {'x': 0.9, 'y': 0.9},
    },
    'threshold': 0.5,
}

response = requests.post(url=f'{URL_HOST}/image/cluster', json=payload)
print(response.json())
