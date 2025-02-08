import requests

URL = 'http://127.0.0.1:5708' # if with webui, the port would be 7860

payload = {
    'dsl': {
        'metaInfo': {
            'userId': 0,
            'sessionId': 0,
        },
        'attributes': [
            {
                'attribute': 'log/image',
                'fileNaming': 'log/image-json',
                'filter': {
                    'type': 'unprocessed',
                    'params': {
                        'name': 'preprocess',
                        'task': 'image_encoding'
                    }
                },
                'strict': False,
            }
        ]
    }
}

response = requests.post(url=f'{URL}/fetch/data', json=payload, timeout=10)
