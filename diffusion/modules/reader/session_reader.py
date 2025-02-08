from .readers import register_reader, readers
from .dsl2api import dsl2api

default_attributes = [
    {
        'attribute': 'log/log',
        'fileNaming': 'log',
        'filter': {
            'type': 'all',
            'params': {}
        }
    },
    {
        'attribute': 'log/image',
        'fileNaming': 'log/image-json',
        'filter': {
            'type': 'all',
            'params': {}
        }
    },
    {
        'attribute': 'preprocess/image_projection',
        'fileNaming': 'log/prompt-json',
        'filter': {
            'type': 'latest',
            'params': {},
            'strict': True
        },
    },
    {
        'attribute': 'preprocess/text_projection',
        'fileNaming': 'log/prompt-json',
        'filter': {
            'type': 'latest',
            'params': {},
            'strict': True
        },
    }
]

@register_reader("session")
class SessionReader:
    def __init__(self, dsl, extensions=[]) -> None:
        self.dsl = dsl
        self.extensions = extensions

        if 'attributes' not in self.dsl:
            self.dsl['attributes'] = default_attributes

    def read(self):
        apis = dsl2api(self.dsl)
        base_reader = readers["base"]

        # check if there is none records
        empty_session = False
        for api in apis:
            if api['attribute']['attribute'] == 'log/log':
                reader = base_reader(**api['api'])
                logs = reader.read()
                if len(logs) == 0:
                    empty_session = True
                    break

        # check if all files exist
        api_list = [api['api'] for api in apis]
        if not empty_session and False in api_list:
            # run extensions
            extensions = sorted(self.extensions)
            for ext in extensions:
                ext.execute()
            apis = dsl2api(self.dsl)

        input_data = {}

        for api in apis:
            if api['api'] is False:
                data = None
            else:
                reader = base_reader(**api['api'])
                data = reader.read(preview=True)
            attribute_name = api['attribute']['attribute']
            input_data[attribute_name] = {
                'attribute': api['attribute'],
                'data': data
            }

        return input_data
