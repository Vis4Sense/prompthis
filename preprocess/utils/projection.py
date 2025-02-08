'''Projection functions'''
import numpy as np
from sklearn.manifold import MDS, TSNE
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0, 1))


def tSNE(vectors, perplexity=5, metric='cosine'):
    '''tSNE'''
    if vectors.shape[0] == 1:
        return np.array([[0.5, 0.5]])
    elif vectors.shape[0] == 2:
        return np.array([[0.3, 0.5], [0.7, 0.5]])

    # perplexity must be less than the number of samples
    perplexity = min(perplexity, vectors.shape[0] - 1)

    # check if all the vectors are the same
    if np.all(vectors == vectors[0]):
        X = np.full((vectors.shape[0], 2), 0.5)
        return X

    tsne = TSNE(n_components=2, perplexity=perplexity, metric=metric)
    tsne.fit_transform(vectors)
    X = tsne.embedding_
    X_norm = scaler.fit_transform(X)

    return X_norm
