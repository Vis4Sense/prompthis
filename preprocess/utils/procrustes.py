'''Use procrustes analysis to align two point sets'''
import numpy as np
from scipy.linalg import orthogonal_procrustes


def align(data1, data2):
    '''Align two point sets using procrustes analysis
    
    Each point is represented as a (key, value) pair.
    Points with the same key between the two sets are aligned.
    
    key is not necessary unique for each point set.
    If several points have the same key, they will be averaged.
    '''

    # get unique key-point dict for each point set
    data1_unique = list2dict(data1)
    data2_unique = list2dict(data2)

    # get common keys
    data1_keys = set(data1_unique.keys())
    data2_keys = set(data2_unique.keys())
    common_keys = list(data1_keys & data2_keys)

    # get reference points and target points
    ref_points = [data1_unique[key] for key in common_keys]
    tgt_points = [data2_unique[key] for key in common_keys]

    if len(ref_points) <= 1 or len(tgt_points) <= 1:
        return data2

    # procrustes analysis
    _, t, norm = procrustes_preprocess(tgt_points)

    try:
        _, _, _, R, s = procrustes(ref_points, tgt_points)
    except ValueError:
        return data2

    # transform target points
    data2_aligned = []
    for key, value in data2:
        pt = np.array(value)
        pt += t
        pt /= norm
        pt = np.dot(pt, R.T) * s
        data2_aligned.append((key, pt.tolist()))

    # normalize aligned points
    data2_array = np.array([value for _, value in data2_aligned])
    min_vals = np.min(data2_array, axis=0)
    max_vals = np.max(data2_array, axis=0)
    normalized_data = (data2_array - min_vals) / (max_vals - min_vals)

    # add key back to the list
    for i, (key, _) in enumerate(data2_aligned):
        data2_aligned[i] = (key, normalized_data[i].tolist())

    return data2_aligned


def list2dict(data):
    '''Merge points with the same key for each point set
    
    This results in a list of points with unique keys
    '''
    data_unique = {}
    for key, value in data:
        if key not in data_unique:
            data_unique[key] = []
        data_unique[key].append(value)

    # average points with the same key
    for key, value in data_unique.items():
        data_unique[key] = np.mean(value, axis=0)

    return data_unique


def procrustes_preprocess(data):
    mtx = np.array(data, dtype=np.double, copy=True)
    t = -np.mean(mtx, 0)
    mtx += t
    norm = np.linalg.norm(mtx)
    mtx /= norm
    return mtx, t, norm


def procrustes(data1, data2):
    r"""Procrustes analysis, a similarity test for two data sets.

    Each input matrix is a set of points or vectors (the rows of the matrix).
    The dimension of the space is the number of columns of each matrix. Given
    two identically sized matrices, procrustes standardizes both such that:

    - :math:`tr(AA^{T}) = 1`.

    - Both sets of points are centered around the origin.

    Procrustes ([1]_, [2]_) then applies the optimal transform to the second
    matrix (including scaling/dilation, rotations, and reflections) to minimize
    :math:`M^{2}=\sum(data1-data2)^{2}`, or the sum of the squares of the
    pointwise differences between the two input datasets.

    This function was not designed to handle datasets with different numbers of
    datapoints (rows).  If two data sets have different dimensionality
    (different number of columns), simply add columns of zeros to the smaller
    of the two.

    Parameters
    ----------
    data1 : array_like
        Matrix, n rows represent points in k (columns) space `data1` is the
        reference data, after it is standardised, the data from `data2` will be
        transformed to fit the pattern in `data1` (must have >1 unique points).
    data2 : array_like
        n rows of data in k space to be fit to `data1`.  Must be the  same
        shape ``(numrows, numcols)`` as data1 (must have >1 unique points).

    Returns
    -------
    mtx1 : array_like
        A standardized version of `data1`.
    mtx2 : array_like
        The orientation of `data2` that best fits `data1`. Centered, but not
        necessarily :math:`tr(AA^{T}) = 1`.
    disparity : float
        :math:`M^{2}` as defined above.

    Raises
    ------
    ValueError
        If the input arrays are not two-dimensional.
        If the shape of the input arrays is different.
        If the input arrays have zero columns or zero rows.

    See Also
    --------
    scipy.linalg.orthogonal_procrustes
    scipy.spatial.distance.directed_hausdorff : Another similarity test
      for two data sets

    Notes
    -----
    - The disparity should not depend on the order of the input matrices, but
      the output matrices will, as only the first output matrix is guaranteed
      to be scaled such that :math:`tr(AA^{T}) = 1`.

    - Duplicate data points are generally ok, duplicating a data point will
      increase its effect on the procrustes fit.

    - The disparity scales as the number of points per input matrix.

    References
    ----------
    .. [1] Krzanowski, W. J. (2000). "Principles of Multivariate analysis".
    .. [2] Gower, J. C. (1975). "Generalized procrustes analysis".

    Examples
    --------
    >>> import numpy as np
    >>> from scipy.spatial import procrustes

    The matrix ``b`` is a rotated, shifted, scaled and mirrored version of
    ``a`` here:

    >>> a = np.array([[1, 3], [1, 2], [1, 1], [2, 1]], 'd')
    >>> b = np.array([[4, -2], [4, -4], [4, -6], [2, -6]], 'd')
    >>> mtx1, mtx2, disparity = procrustes(a, b)
    >>> round(disparity)
    0.0

    """
    mtx1 = np.array(data1, dtype=np.double, copy=True)
    mtx2 = np.array(data2, dtype=np.double, copy=True)

    if mtx1.ndim != 2 or mtx2.ndim != 2:
        raise ValueError("Input matrices must be two-dimensional")
    if mtx1.shape != mtx2.shape:
        raise ValueError("Input matrices must be of same shape")
    if mtx1.size == 0:
        raise ValueError("Input matrices must be >0 rows and >0 cols")

    # translate all the data to the origin
    mtx1 -= np.mean(mtx1, 0)
    mtx2 -= np.mean(mtx2, 0)

    norm1 = np.linalg.norm(mtx1)
    norm2 = np.linalg.norm(mtx2)

    if norm1 == 0 or norm2 == 0:
        raise ValueError("Input matrices must contain >1 unique points")

    # change scaling of data (in rows) such that trace(mtx*mtx') = 1
    mtx1 /= norm1
    mtx2 /= norm2

    # transform mtx2 to minimize disparity
    R, s = orthogonal_procrustes(mtx1, mtx2)
    mtx2 = np.dot(mtx2, R.T) * s

    # measure the dissimilarity between the two datasets
    disparity = np.sum(np.square(mtx1 - mtx2))

    return mtx1, mtx2, disparity, R, s
