import os
import sys

cur_path = os.path.abspath(__file__)
cur_dir = os.path.dirname(cur_path)
parent_dir = os.path.dirname(cur_dir)
sys.path.append(parent_dir)

print(sys.path)

from modules.image_encoding.clip_encoding import clip_text_embeddings

texts = [
    'a diagram',
    'a dog',
    'a cat',
]

vectors = clip_text_embeddings(texts)

print(vectors.shape)
print(vectors[0][:10])
print(vectors[1][:10])
print(vectors[2][:10])
