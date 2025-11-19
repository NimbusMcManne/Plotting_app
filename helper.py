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

    def sort_points_clockwise(self, coords):
        if not coords or len(coords) < 2:
            return coords

        coords_array = np.array(coords)

        # Calculate centroid
        centroid = np.mean(coords_array, axis=0)

        # Calculate angle for each point relative to centroid
        angles = []
        for point in coords_array:
            # Vector from centroid to point
            dx = point[0] - centroid[0]
            dy = point[1] - centroid[1]
            angle = np.arctan2(dy, dx)
            angles.append(angle)

        # Sort by angle in descending order for clockwise
        sorted_indices = np.argsort(angles)[::-1]
        sorted_coords = coords_array[sorted_indices].tolist()

        return sorted_coords