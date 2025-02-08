import numpy as np

from utils.procrustes import align
from utils.projection import tSNE
from .processors import register_processor
from .base_processor import BaseProcessor


@register_processor("image_projection")
class ImageProjectionProcessor(BaseProcessor):
    '''Processor for embedding images to a 2D space.'''

    def process(self):
        ''' Embedding images.

        self.input_data is a dictionary with the following keys:
        - 'preprocess/image_encoding':
            - 'attribute': attribute configuration
            - 'data': a list of image encoding, each is a dictionary:
                - 'filename': image filename
                - 'data': image embedding
        - 'preprocess/image_projection':
            - 'attribute': attribute configuration
            - 'data': a dictionary
                - key: image filename
                - value: 2D coordinates of the image
        '''
        image_data = self.input_data["preprocess/image_encoding"]["data"]

        embeddings = [image["data"] for image in image_data]
        embeddings = np.array(embeddings)
        points = tSNE(embeddings)

        output_data = {}
        for idx, item in enumerate(image_data):
            filename = item["filename"]
            value = points[idx].tolist()
            output_data[filename] = value

        previous_projection = self.input_data["preprocess/image_projection"]["data"]
        if previous_projection is None:
            return output_data

        # input matrices for procrustes must have contain >1 unique points
        if len(previous_projection) <= 1:
            return output_data

        # align the new projection with the previous one
        ref_data = list(previous_projection.items())
        tgt_data = list(output_data.items())

        tgt_data = align(ref_data, tgt_data)
        tgt_data = dict(tgt_data)

        return tgt_data
