import copy

from .processors import register_processor
from .base_processor import BaseProcessor
from .image_encoding.clip_encoding import clip_text_embeddings


@register_processor("text_encoding")
class TextEncodingProcessor(BaseProcessor):
    def process(self):
        print('text encoding called')
        input_data = self.input_data['log/setting']['data']

        texts = []
        for item in input_data:
            if 'parameters' in item['data']:
                texts.append(item['data']['parameters']['prompt'])
            else:
                texts.append(item['data']['prompt'])

        if len(texts) == 0:
            return []

        embeddings = clip_text_embeddings(texts)

        output_data = []
        for idx, item in enumerate(input_data):
            item_ = copy.deepcopy(item)
            item_['data'] = embeddings[idx].tolist()
            output_data.append(item_)

        return output_data
