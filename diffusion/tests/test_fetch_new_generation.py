import requests

URL = "http://127.0.0.1:5708" # if with webui, the port would be 7860

payload = {
    "dsl": {
        "data": {
            "user_id": None,
            "thread_id": None,
        },
        "prompt_id": 133,
    }
}

# for i in range(10):
for i in range(1):
    response = requests.post(url=f'{URL}/fetch/new_generation', json=payload)
    print(response.text)
