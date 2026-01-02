import numpy as np
from helper import HELPER

class SHAPE:

    def __init__(self):
        self.helper = HELPER()
        pass

    # Splits figure for better shape similarity measure
    def split_figure_horizontally(self, coords):
        coords = self.helper._rotate_coords_pca(coords)
        arr = np.asarray(coords, dtype=float)
        if arr.size == 0:
            return [], []
        if arr.ndim != 2 or arr.shape[1] < 2:
            raise ValueError(f"Expected coords shaped (n, 2), got {arr.shape}")
        pos_indices = np.where(arr[:, 1] >= 0)[0]
        neg_indices = np.where(arr[:, 1] < 0)[0]
    
        pos_coords = arr[pos_indices].tolist()
        neg_coords = arr[neg_indices].tolist()

        pos_coords = self.helper.center_coords_at_origin(pos_coords)
        neg_coords = self.helper.center_coords_at_origin(neg_coords)

        return pos_coords, neg_coords

    def split_figure_vertically(self, coords):
        coords = self.helper._rotate_coords_pca(coords)
        arr = np.asarray(coords, dtype=float)
        if arr.size == 0:
            return [], []
        if arr.ndim != 2 or arr.shape[1] < 2:
            raise ValueError(f"Expected coords shaped (n, 2), got {arr.shape}")
        right_indices = np.where(arr[:, 0] >= 0)[0]
        left_indices = np.where(arr[:, 0] < 0)[0]
        
        right_coords = arr[right_indices].tolist()
        left_coords = arr[left_indices].tolist()

        right_coords = self.helper.center_coords_at_origin(right_coords)
        left_coords = self.helper.center_coords_at_origin(left_coords)
        
        return right_coords, left_coords
    
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
    def construct_half_ellipse_horizontal(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side not in ('pos', 'neg'):
            raise ValueError("side must be 'pos' or 'neg'")
        if side == 'pos':
            # Upper half: angles from 0 to π
            angles = np.linspace(0, np.pi, num_points, endpoint=False)
        else:  # side == 'neg'
            # Lower half: angles from π to 2π
            angles = np.linspace(np.pi, 2 * np.pi, num_points, endpoint=False)
        ellipse_points = np.column_stack((
            cx + (width / 2.0) * np.cos(angles),
            cy + (height / 2.0) * np.sin(angles)
        ))
        return ellipse_points


    def construct_half_ellipse_vertical(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side not in ('pos', 'neg'):
            raise ValueError("side must be 'pos' or 'neg'")
        
        if side == 'pos':
            # Right half: angles from -π/2 to π/2
            angles = np.linspace(-0.5 * np.pi, 0.5 * np.pi, num_points, endpoint=False)
        else:  # side == 'neg'
            # Left half: angles from π/2 to 3π/2
            angles = np.linspace(0.5 * np.pi, 1.5 * np.pi, num_points, endpoint=False)
        
        ellipse_points = np.column_stack((
            cx + (width / 2.0) * np.cos(angles),
            cy + (height / 2.0) * np.sin(angles)
        ))
        return ellipse_points
    

    def construct_half_diamond_horizontal(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side not in ('pos', 'neg'):
            raise ValueError("side must be 'pos' or 'neg'")

        half_width = width / 2.0
        half_height = height / 2.0

        right = np.array([cx + half_width, cy], dtype=float)
        apex = np.array([cx, cy + half_height], dtype=float) if side == 'pos' else np.array([cx, cy - half_height], dtype=float)
        left = np.array([cx - half_width, cy], dtype=float)

        if num_points == 1:
            return np.array([apex], dtype=float)

        seg1 = apex - right
        seg2 = left - apex
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
                point = right + t * seg1
            else:
                remaining = dist - len1
                t = 0.0 if len2 == 0 else remaining / len2
                point = apex + t * seg2
            points.append(point)

        return np.asarray(points, dtype=float)
    

    def construct_half_diamond_vertical(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side not in ('pos', 'neg'):
            raise ValueError("side must be 'pos' or 'neg'")

        half_width = width / 2.0
        half_height = height / 2.0

        # For vertical split: top and bottom points on y-axis
        top = np.array([cx, cy + half_height], dtype=float)
        apex = np.array([cx + half_width, cy], dtype=float) if side == 'pos' else np.array([cx - half_width, cy], dtype=float)
        bottom = np.array([cx, cy - half_height], dtype=float)

        if num_points == 1:
            return np.array([apex], dtype=float)

        # Two segments: top→apex and apex→bottom
        seg1 = apex - top
        seg2 = bottom - apex
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
                point = apex + t * seg2
            points.append(point)

        return np.asarray(points, dtype=float)
    


    def construct_rectangle(self, width, height, num_points, cx=0.0, cy=0.0):
        """Construct a rectangle outline with evenly spaced points."""
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        
        half_w = width / 2.0
        half_h = height / 2.0
        
        # Four corners
        corners = [
            [cx - half_w, cy + half_h],  # top-left
            [cx + half_w, cy + half_h],  # top-right
            [cx + half_w, cy - half_h],  # bottom-right
            [cx - half_w, cy - half_h],  # bottom-left
        ]
        
        # Calculate perimeter
        perimeter = 2 * (width + height)
        distances = np.linspace(0.0, perimeter, num_points, endpoint=False)
        
        points = []
        for dist in distances:
            # Normalize distance to [0, perimeter)
            dist = dist % perimeter
            
            if dist < width:  # Top edge
                t = dist / width
                point = [corners[0][0] + t * width, corners[0][1]]
            elif dist < width + height:  # Right edge
                t = (dist - width) / height
                point = [corners[1][0], corners[1][1] - t * height]
            elif dist < 2 * width + height:  # Bottom edge
                t = (dist - width - height) / width
                point = [corners[2][0] - t * width, corners[2][1]]
            else:  # Left edge
                t = (dist - 2 * width - height) / height
                point = [corners[3][0], corners[3][1] + t * height]
            
            points.append(point)
        
        return np.asarray(points, dtype=float)

    def construct_half_rectangle_horizontal(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        """Construct horizontal half-rectangle (top or bottom).
        
        side: 'pos' for top half, 'neg' for bottom half
        """
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side not in ('pos', 'neg'):
            raise ValueError("side must be 'pos' or 'neg'")
        
        half_w = width / 2.0
        half_h = height / 2.0
        
        if side == 'pos':
            # Top half: top-left → top-right → center-right → center-left
            top_left = np.array([cx - half_w, cy + half_h], dtype=float)
            top_right = np.array([cx + half_w, cy + half_h], dtype=float)
            center_right = np.array([cx + half_w, cy], dtype=float)
            center_left = np.array([cx - half_w, cy], dtype=float)
            
            seg1 = top_right - top_left
            seg2 = center_right - top_right
            seg3 = center_left - center_right
        else:
            # Bottom half: center-left → center-right → bottom-right → bottom-left
            center_left = np.array([cx - half_w, cy], dtype=float)
            center_right = np.array([cx + half_w, cy], dtype=float)
            bottom_right = np.array([cx + half_w, cy - half_h], dtype=float)
            bottom_left = np.array([cx - half_w, cy - half_h], dtype=float)
            
            seg1 = center_right - center_left
            seg2 = bottom_right - center_right
            seg3 = bottom_left - bottom_right
        
        len1 = np.linalg.norm(seg1)
        len2 = np.linalg.norm(seg2)
        len3 = np.linalg.norm(seg3)
        total_len = len1 + len2 + len3
        
        if total_len == 0:
            return np.repeat([[cx, cy]], num_points, axis=0)
        
        distances = np.linspace(0.0, total_len, num_points)
        points = []
        
        for dist in distances:
            if dist <= len1:
                t = dist / len1 if len1 > 0 else 0
                point = (top_left if side == 'pos' else center_left) + t * seg1
            elif dist <= len1 + len2:
                t = (dist - len1) / len2 if len2 > 0 else 0
                point = (top_right if side == 'pos' else center_right) + t * seg2
            else:
                t = (dist - len1 - len2) / len3 if len3 > 0 else 0
                point = (center_right if side == 'pos' else bottom_right) + t * seg3
            
            points.append(point)
        
        return np.asarray(points, dtype=float)

    def construct_half_rectangle_vertical(self, width, height, num_points, side='pos', cx=0.0, cy=0.0):
        """Construct vertical half-rectangle (right or left).
        
        side: 'pos' for right half, 'neg' for left half
        """
        if num_points <= 0:
            return np.empty((0, 2), dtype=float)
        if side not in ('pos', 'neg'):
            raise ValueError("side must be 'pos' or 'neg'")
        
        half_w = width / 2.0
        half_h = height / 2.0
        
        if side == 'pos':
            # Right half: top-right → bottom-right → center-bottom → center-top
            top_right = np.array([cx + half_w, cy + half_h], dtype=float)
            bottom_right = np.array([cx + half_w, cy - half_h], dtype=float)
            center_bottom = np.array([cx, cy - half_h], dtype=float)
            center_top = np.array([cx, cy + half_h], dtype=float)
            
            seg1 = bottom_right - top_right
            seg2 = center_bottom - bottom_right
            seg3 = center_top - center_bottom
        else:
            # Left half: top-left → center-top → center-bottom → bottom-left
            top_left = np.array([cx - half_w, cy + half_h], dtype=float)
            center_top = np.array([cx, cy + half_h], dtype=float)
            center_bottom = np.array([cx, cy - half_h], dtype=float)
            bottom_left = np.array([cx - half_w, cy - half_h], dtype=float)
            
            seg1 = center_top - top_left
            seg2 = center_bottom - center_top
            seg3 = bottom_left - center_bottom
        
        len1 = np.linalg.norm(seg1)
        len2 = np.linalg.norm(seg2)
        len3 = np.linalg.norm(seg3)
        total_len = len1 + len2 + len3
        
        if total_len == 0:
            return np.repeat([[cx, cy]], num_points, axis=0)
        
        distances = np.linspace(0.0, total_len, num_points)
        points = []
        
        for dist in distances:
            if dist <= len1:
                t = dist / len1 if len1 > 0 else 0
                point = (top_right if side == 'pos' else top_left) + t * seg1
            elif dist <= len1 + len2:
                t = (dist - len1) / len2 if len2 > 0 else 0
                point = (bottom_right if side == 'pos' else center_top) + t * seg2
            else:
                t = (dist - len1 - len2) / len3 if len3 > 0 else 0
                point = (center_bottom if side == 'pos' else center_bottom) + t * seg3
            
            points.append(point)
        
        return np.asarray(points, dtype=float)