import numpy as np
from helper import HELPER

class SHAPE:

    def __init__(self):
        self.helper = HELPER()
        pass

    # Splits figure for better shape similarity measure
    def split_figure(self, coords):
        coords = self.helper._rotate_coords_pca(coords)
        arr = np.asarray(coords, dtype=float)
        if arr.size == 0:
            return [], []
        if arr.ndim != 2 or arr.shape[1] < 2:
            raise ValueError(f"Expected coords shaped (n, 2), got {arr.shape}")
        pos_coords = arr[arr[:, 1] >= 0].tolist()
        neg_coords = arr[arr[:, 1] <= 0].tolist()
        return pos_coords, neg_coords

    # Constructs ellipses datapoints
    def construct_ellipse(self, width, height, num_points, cx=0.0, cy=0.0):
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        ellipse_points = np.column_stack((
            cx + (width / 2.0) * np.cos(angles),
            cy + (height / 2.0) * np.sin(angles)
        ))
        return ellipse_points

    # Constructs half-ellipse datapoints
    # side: 'pos' for right half (x >= 0), 'neg' for left half (x <= 0)
    def construct_half_ellipse(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side == 'pos':
            # Right half: angles from -π/2 to π/2
            angles = np.linspace(-np.pi / 2, np.pi / 2, num_points, endpoint=False)
        else:  # side == 'neg'
            # Left half: angles from π/2 to 3π/2
            angles = np.linspace(np.pi / 2, 3 * np.pi / 2, num_points, endpoint=False)
        ellipse_points = np.column_stack((
            cx + (width / 2.0) * np.cos(angles),
            cy + (height / 2.0) * np.sin(angles)
        ))
        return ellipse_points

    
    def construct_half_diamond(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side not in ('pos', 'neg'):
            raise ValueError("side must be 'pos' or 'neg'")

        half_width = width / 2.0
        half_height = height / 2.0

        top = np.array([cx, cy + half_height], dtype=float)
        mid = np.array([cx + half_width, cy], dtype=float) if side == 'pos' else np.array([cx - half_width, cy], dtype=float)
        bottom = np.array([cx, cy - half_height], dtype=float)

        if num_points == 1:
            return np.array([top], dtype=float)

        seg1 = mid - top
        seg2 = bottom - mid
        len1 = np.linalg.norm(seg1)
        len2 = np.linalg.norm(seg2)
        total_len = len1 + len2

        if total_len == 0:
            return np.repeat([[cx, cy]], num_points, axis=0)

        distances = np.linspace(0.0, total_len, num_points)
        points = []
        for dist in distances:
            if dist <= len1 or len2 == 0:
                t = 0.0 if len1 == 0 else dist / len1
                point = top + t * seg1
            else:
                remaining = dist - len1
                t = 0.0 if len2 == 0 else remaining / len2
                point = mid + t * seg2
            points.append(point)

        return np.asarray(points, dtype=float)