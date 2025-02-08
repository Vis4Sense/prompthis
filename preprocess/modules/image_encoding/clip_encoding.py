import os
import sys
import json

import torch
import numpy as np

from . import clip

# Get the parent directory of the current script (text-image-diff)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the parent directory to the Python path
sys.path.append(parent_dir)

# preparation
clip.available_models()
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

model.cuda().eval()
input_resolution = model.visual.input_resolution
context_length = model.context_length
vocab_size = model.vocab_size

print("device:", device)
print("Model parameters:", f"{np.sum([int(np.prod(p.shape)) for p in model.parameters()]):,}")
print("Input resolution:", input_resolution)
print("Context length:", context_length)
print("Vocab size:", vocab_size)


def clip_embeddings(images):
    print("images:", len(images))

    images_ = []

    for image in images:
        image_ = preprocess(image).unsqueeze(0).to(device)
        images_.append(image_)

    if len(images) == 1:
        images_.append(images_[0])

    with torch.no_grad():
        images_ = torch.stack(images_).to(device)
        images_ = torch.squeeze(images_)
        vectors = model.encode_image(images_)
        vectors = vectors.cpu()
        vectors = vectors.detach().numpy()

    if len(images) == 1:
        vectors = vectors[:1]

    return vectors


def clip_text_embeddings(texts):
    print("texts:", len(texts))

    texts_ = []

    for text in texts:
        text_ = clip.tokenize(text, truncate=True).to(device)
        texts_.append(text_)

    if len(texts) == 1:
        texts_.append(texts_[0])

    with torch.no_grad():
        texts_ = torch.stack(texts_).to(device)
        texts_ = torch.squeeze(texts_)
        vectors = model.encode_text(texts_)
        vectors = vectors.cpu()
        vectors = vectors.detach().numpy()

    if len(texts) == 1:
        vectors = vectors[:1]

    return vectors
