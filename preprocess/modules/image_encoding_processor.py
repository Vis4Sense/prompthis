'''Image encoding processor.'''
import copy
import base64
from io import BytesIO
from PIL import Image

from .processors import register_processor
from .base_processor import BaseProcessor
from .image_encoding.clip_encoding import clip_embeddings


@register_processor("image_encoding")
class ImageEncodingProcessor(BaseProcessor):
    '''Processor for encoding images.'''

    def process(self):
        '''
        Encoding images.

        self.input_data is a dictionary with the following keys:
        - 'log/image':
            - 'attribute': attribute configuration
            - 'data': a list of images, each is a dictionary:
                - 'filename': image filename
                - 'data': base64 encoded image
        '''

        def open_image(base64_data):
            return Image.open(BytesIO(base64.b64decode(base64_data)))

        input_data = self.input_data["log/image"]["data"]
        images = []
        for item in input_data:
            images.append(open_image(item["data"]))

        if len(images) == 0:
            return []

        embeddings = clip_embeddings(images)

        output_data = []
        for idx, item in enumerate(input_data):
            item_ = copy.deepcopy(item)
            item_["data"] = embeddings[idx].tolist()
            output_data.append(item_)

        return output_data
