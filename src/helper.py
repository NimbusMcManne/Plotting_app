from sklearn.decomposition import PCA
from shapesimilarity.procrustesanalysis import rotate_curve, find_procrustes_rotation_angle
from shapesimilarity.frechetdistance import frechet_distance
from shapesimilarity.geometry import curve_length
import math
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
        coords_array = np.array(coords)
        
        if coords_array.size == 0 or len(coords_array) < 2:
            return coords_array.tolist()

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

    
    # def raw_shape_similarity(self, shape1, shape2, rotations=10, align_rotation=True):
    #     curve1 = np.asarray(shape1, dtype=float)
    #     curve2 = np.asarray(shape2, dtype=float)

    #     # optional: translate only (skip scaling)
    #     # curve1 = curve1 - curve1.mean(axis=0)
    #     # curve2 = curve2 - curve2.mean(axis=0)


    #     geo_avg_curve_len = math.sqrt(curve_length(curve1) * curve_length(curve2))
    #     thetas = [0.0]
    #     if align_rotation:
    #         # this helper needs normalized curves, so call it on your shifted copies
    #         theta = find_procrustes_rotation_angle(curve1, curve2)
    #         thetas.append(theta)
    #         for i in range(rotations):
    #             theta = -math.pi + (2 * i * math.pi) / max(rotations - 1, 1)
    #             if theta not in (0, math.pi):
    #                 thetas.append(theta)

    #     min_dist = float("inf")
    #     for theta in thetas:
    #         rotated = rotate_curve(curve1, theta)
    #         min_dist = min(min_dist, frechet_distance(rotated, curve2))

    #     return max(1 - min_dist / (geo_avg_curve_len / math.sqrt(2)), 0)
    

    def center_coords_at_origin(self, coords):
        coords_array = np.asarray(coords, dtype=float)
        
        if coords_array.size == 0 or len(coords_array) == 0:
            return coords_array
        
        # Calculate centroid
        centroid = np.mean(coords_array, axis=0)
        
        # Center at origin by subtracting centroid
        centered = coords_array - centroid
        
        return centered



    def raw_shape_similarity(self, shape1, shape2, rotations=10, align_rotation=True):
        curve1 = np.asarray(shape1, dtype=float)
        curve2 = np.asarray(shape2, dtype=float)

        # Compute bounding box sizes (scale measure)
        bbox1 = np.max(curve1, axis=0) - np.min(curve1, axis=0)
        bbox2 = np.max(curve2, axis=0) - np.min(curve2, axis=0)
        size1 = np.linalg.norm(bbox1)
        size2 = np.linalg.norm(bbox2)
        
        # Scale penalty: penalize large size differences
        size_ratio = min(size1, size2) / max(size1, size2) if max(size1, size2) > 0 else 0
        scale_penalty = size_ratio ** 2  # Squared to penalize more aggressively
        
        # Raw Fréchet distance without normalization
        thetas = [0.0]
        if align_rotation:
            theta = find_procrustes_rotation_angle(curve1, curve2)
            thetas.append(theta)
            for i in range(rotations):
                theta = -np.pi + (2 * i * np.pi) / max(rotations - 1, 1)
                if theta not in (0, np.pi):
                    thetas.append(theta)

        min_dist = float("inf")
        for theta in thetas:
            rotated = rotate_curve(curve1, theta)
            min_dist = min(min_dist, frechet_distance(rotated, curve2))

        # Normalize by average size (not curve length) and apply scale penalty
        avg_size = (size1 + size2) / 2.0
        if avg_size == 0:
            return 0.0
        
        normalized_dist = min_dist / avg_size
        similarity = max(1 - normalized_dist, 0) * scale_penalty
        
        return similarity