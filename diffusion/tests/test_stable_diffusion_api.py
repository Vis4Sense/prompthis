import requests

URL = "http://127.0.0.1:7861" # if with webui, the port would be 7860

payload = {
    "prompt": "dog",
}

response = requests.post(url=f'{URL}/sdapi/v1/txt2img', json=payload)
data = response.json()
print(data.keys())
