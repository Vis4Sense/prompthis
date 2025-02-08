import requests

URL = "http://127.0.0.1:5708" # if with webui, the port would be 7860

payload = {
    'userId': 0,
}

for i in range(1):
    response = requests.post(url=f'{URL}/create/session', json=payload)
    print(response.json())
