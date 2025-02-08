from scipy.cluster.hierarchy import linkage, dendrogram, fcluster


def image_cluster(embeddings: dict, threshold=1):
    '''Cluster images
    
    Args:
        embeddings (dict): a dictionary of image embeddings,
            e.g. {'i1': {'x': 0.1, 'y': 0.1}, 'i2': {'x': 0.2, 'y': 0.2}, ...}
        threshold (float): the threshold for clustering
    '''
    point_list = list(embeddings.items())
    points = [value for _, value in point_list]
    points = [[val['x'], val['y']] for val in points]
    clusters = cluster(points, threshold)
    result = { key: clusters[i] for i, (key, _) in enumerate(point_list)}
    return result


def cluster(points, threshold=1):
    '''Given a list of 2d points, cluster them into groups.
    
    Args:
        points (list): a list of 2d points, e.g. [[1, 2], [3, 4], ...]
        threshold (float): the threshold for clustering
    '''
    Z = linkage(points, method='ward')
    clusters = fcluster(Z, t=threshold, criterion='distance').tolist()
    return clusters
