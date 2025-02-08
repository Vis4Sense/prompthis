'''Embedding prompts to 2D space.'''
import os
import numpy as np

from utils.projection import tSNE
from utils.procrustes import align
from .processors import register_processor
from .base_processor import BaseProcessor


@register_processor('text_projection')
class TextProjectionProcessor(BaseProcessor):
    '''Processor for embedding prompts to 2D space.'''

    def process(self):
        '''Embedding prompts.

        The prompt embedding is aligned with the image embedding.
        
        self.input_data is a dictionary with the following keys:
        - 'log/log':
            - 'attribute': attribute configuration
            - 'data': a list of interation records
        - 'preprocess/text_encoding':
            - 'attribute': attribute configuration
            - 'data': a list of text encoding, each is a dictionary:
                - 'filename': setting filename
                - 'data': text embedding
        - 'preprocess/image_projection':
            - 'attribute': attribute configuration
            - 'data': a dictionary
                - key: image filename
                - value: 2D coordinates of the image
        '''
        text_data = self.input_data['preprocess/text_encoding']['data']

        embeddings = [text['data'] for text in text_data]
        embeddings = np.array(embeddings)
        points = tSNE(embeddings)

        output_data = {}
        for idx, item in enumerate(text_data):
            filename = item['filename']
            value = points[idx].tolist()
            output_data[filename] = value

        image_projection = self.input_data['preprocess/image_projection']['data']
        if image_projection is None:
            return output_data

        # input matrices for procrustes must have contain >1 unique points
        if len(image_projection) <= 1:
            return output_data

        # log data
        logs = self.input_data['log/log']['data']

        # transform output_data and image projection to (key, value) list
        tgt_data = []
        ref_data = []

        prompt_id_dict = {}

        for item in logs:
            # key is the prompt_id in log
            prompt_id = item['prompt_id']
            setting_filename = item['setting_filename']
            output_filenames = item['output_filenames']

            if setting_filename in output_data:
                value = output_data[setting_filename]
                tgt_data.append((prompt_id, value))
                prompt_id_dict[prompt_id] = setting_filename

            for image_filename in output_filenames:
                image_projection_filename = os.path.splitext(image_filename)[0] + '.json'
                if image_projection_filename in image_projection:
                    value = image_projection[image_projection_filename]
                    ref_data.append((prompt_id, value))

        # align text projection with image projection
        tgt_data = align(ref_data, tgt_data)
        tgt_data = {prompt_id_dict[key]: value for key, value in tgt_data}

        return tgt_data
