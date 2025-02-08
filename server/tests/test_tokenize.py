import requests

URL = "https://vis.pku.edu.cn/prompthis"


payload = {
    'prompts': [
        { 'prompt': 'maple in the snow' },
        { 'prompt': 'Dewdrops on maple leaves' },
        { 'prompt': 'forest in the snowy winter' }
    ],
}

response = requests.post(url=f'{URL}/prompt/tokenize', json=payload)
print(response.json())
