"""
===========================================
Sparse coding with a precomputed dictionary
===========================================

Transform a signal as a sparse combination of Ricker wavelets. This example
visually compares different sparse coding methods using the
:class:`sklearn.decomposition.SparseCoder` estimator.
"""
print __doc__

import numpy as np
import matplotlib.pylab as pl

from sklearn.decomposition import SparseCoder


def ricker_function(resolution, center, width):
    """Discrete sub-sampled Ricker (mexican hat) wavelet"""
    x = np.linspace(0, resolution - 1, resolution)
    x = (2 / ((np.sqrt(3 * width) * np.pi ** 1 / 4))) * (
         1 - ((x - center) ** 2 / width ** 2)) * np.exp(
         (-(x - center) ** 2) / (2 * width ** 2))
    return x


def ricker_matrix(width, resolution, n_atoms):
    """Dictionary of Ricker (mexican hat) wavelets"""
    centers = np.linspace(0, resolution - 1, n_atoms)
    D = np.empty((n_atoms, resolution))
    for i, center in enumerate(centers):
        D[i] = ricker_function(resolution, center, width)
    D /= np.sqrt(np.sum(D ** 2, axis=1))[:, np.newaxis]
    return D


resolution = 1024
subsampling = 3  # subsampling factor
width = 50
n_atoms = resolution / subsampling

# Compute a wavelet dictionary
D = ricker_matrix(width=width, resolution=resolution, n_atoms=n_atoms)

# Generate a signal
y = np.linspace(0, resolution - 1, resolution)
first_quarter = y < resolution / 4
y[first_quarter] = 3.0
y[np.logical_not(first_quarter)] = 0.

# List the different sparse coding methods in the following format:
# (title, transform_algorithm, transform_alpha, transform_n_nozero_coefs)
estimators = [('OMP', 'omp', None, 15),
              ('Lasso', 'lasso_cd', 1, None),
]

pl.figure()
pl.plot(y, ls='dotted', label='Original signal')
# Do a wavelet approximation
for title, algo, alpha, n_nonzero in estimators:
    coder = SparseCoder(dictionary=D, transform_n_nonzero_coefs=n_nonzero,
                        transform_alpha=alpha, transform_algorithm=algo)
    x = coder.transform(y)
    density = len(np.flatnonzero(x))
    pl.plot(np.ravel(np.dot(x, D)), label=title + ': %s nonzero coefs' % density)

# Soft thresholding debiasing
coder = SparseCoder(dictionary=D, transform_algorithm='threshold',
                    transform_alpha=8)
x = coder.transform(y)
_, idx = np.where(x != 0)
x[0, idx], _, _, _ = np.linalg.lstsq(D[idx, :].T, y)
pl.plot(np.ravel(np.dot(x, D)), 
        label='Thresholding w/ debiasing:\n%d nonzero coefs' % len(idx))
pl.axis('tight')
pl.legend()
pl.show()