from sklearn.decomposition import PCA
import numpy as np
import ezdxf as dxf
import os
import sys

class HELPER:

    def __init__(self):
        pass

    def _rotate_coords_pca(self, coords):
        pca = PCA(n_components=2)
        pca.fit(coords)
        rotated = pca.transform(coords)
        return rotated