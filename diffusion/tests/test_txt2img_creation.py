import requests

URL = "http://127.0.0.1:5708" # if with webui, the port would be 7860

payload = {
    "model": "stable-diffusion-webui",
    'user_id': 0,
    # 'thread_id': 0,
    "settings": {
        "prompt": "A photo of a cat",
        "steps": 20
    }
}

# for i in range(10):
for i in range(1):
    response = requests.post(url=f'{URL}/create/txt2img', json=payload)
    print(response.text)
