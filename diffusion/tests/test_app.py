import requests

URL = "http://127.0.0.1:5708" # if with webui, the port would be 7860

response = requests.get(url=f'{URL}/hello_world', json=None)
print(response.text)

