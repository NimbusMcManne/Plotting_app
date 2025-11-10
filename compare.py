import numpy as np
import os
import sys
from scipy.spatial.distance import cdist
from shapesimilarity import shape_similarity
from plotting import PLOT

class COMPARE:
    def __init__(self, dxf_folder, BASE_DIR):
        self.BASE_DIR = BASE_DIR
        self.dxf_folder = dxf_folder
        self.c = PLOT(dxf_folder, BASE_DIR)
        self.ellipse_areas = dict()
        self.ellipse_circumference = dict()
        self.figure_areas = dict()
        self.figure_circumference = dict()
        self.ellipse_similarity = dict()
    
    def get_ellipse_similarities(self):
        return self.ellipse_similarity

    def get_ellipse_circumferences(self):

        def circumference(a, b):
            h = (a-b)**2 / (a+b)**2
            c = np.pi*(a+b)*(1+(3*h)/10+np.sqrt(4-3*h))
            return c

        ellipse = self.c.get_ellipse_width_height()
        if not ellipse:
            if not self.c.get_coordinates():
                self.c.read_file()
                self.c.to_array(center_at_origin=True)

            self.c.compute_ellipse_dimensions()
            ellipse = self.c.get_ellipse_width_height()
        for name, (width, height) in ellipse.items():
            self.ellipse_circumference[name] = circumference(width/2, height/2)
    
    def get_ellipse_areas(self):
        ellipse = self.c.get_ellipse_width_height()
        if not ellipse:
            if not self.c.get_coordinates():
                self.c.read_file()
                self.c.to_array(center_at_origin=True)

            self.c.compute_ellipse_dimensions()
            ellipse = self.c.get_ellipse_width_height()
        for name, (width, height) in ellipse.items():
            self.ellipse_areas[name] = float(np.pi * (width * 0.5) * (height * 0.5))


    def get_figure_areas(self):
        coords_by_name = self.c.get_coordinates()
        if not coords_by_name:
            print("coords not found")
            self.c.read_file()
            self.c.to_array(center_at_origin=False)
            coords_by_name = self.c.get_coordinates()

        def monotone_chain_convex_hull(points):
            pts = sorted(points)
            if len(pts) <= 1:
                return pts

            def cross(o, a, b):
                return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

            lower = []
            for p in pts:
                while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                    lower.pop()
                lower.append(p)

            upper = []
            for p in reversed(pts):
                while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                    upper.pop()
                upper.append(p)

            return lower[:-1] + upper[:-1]

        def shoelace_area(poly):
            if len(poly) < 3:
                return 0.0
            arr = np.asarray(poly, dtype=float)
            x = arr[:, 0]
            y = arr[:, 1]
            return float(0.5 * np.abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))

        figure_areas = {}
        for name, pts in coords_by_name.items():
            if not pts or len(pts) < 3:
                figure_areas[name] = 0.0
                continue
            hull = monotone_chain_convex_hull(pts)
            figure_areas[name] = shoelace_area(hull)
            self.figure_areas = figure_areas


    def get_figure_circumferences(self):
        coords_by_name = self.c.get_coordinates()
        if not coords_by_name:
            self.c.read_file()
            self.c.to_array(center_at_origin=False)
            coords_by_name = self.c.get_coordinates()

        def monotone_chain_convex_hull(points):
            pts = sorted(points)
            if len(pts) <= 1:
                return pts

            def cross(o, a, b):
                return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

            lower = []
            for p in pts:
                while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
                    lower.pop()
                lower.append(p)

            upper = []
            for p in reversed(pts):
                while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
                    upper.pop()
                upper.append(p)

            return lower[:-1] + upper[:-1]

        def perimeter(poly):
            if len(poly) < 2:
                return 0.0
            arr = np.asarray(poly, dtype=float)
            diffs = arr[(np.arange(len(arr)) + 1) % len(arr)] - arr
            seg_lengths = np.sqrt((diffs[:, 0] ** 2) + (diffs[:, 1] ** 2))
            return float(seg_lengths.sum())

        figure_perimeters = {}
        for name, pts in coords_by_name.items():
            if not pts or len(pts) < 2:
                figure_perimeters[name] = 0.0
                continue
            hull = monotone_chain_convex_hull(pts)
            figure_perimeters[name] = perimeter(hull)
            self.figure_circumference[name] = figure_perimeters[name]


    def compare_circumferences(self):
        for name, circumference in self.ellipse_circumference.items():
            difference = self.figure_circumference[name] / circumference
            precentage = 100 * difference
            print(f"{name} is {precentage}% ellipse")
    

    def compare_areas(self):
        for name, area in self.ellipse_areas.items():
            difference = self.figure_areas[name] / area
            precentage = 100 * difference
            print(f"{name} is {precentage}% ellipse")


    # def get_ellipse_shape_similarities(self, num_samples=400):
    #     coords_by_name = self.c.get_coordinates()
    #     if not coords_by_name:
    #         self.c.read_file()
    #         # Center at origin improves PCA stability for similarity
    #         self.c.to_array(center_at_origin=True)
    #         coords_by_name = self.c.get_coordinates()

    #     # Ensure ellipse width/height exist (computed in PCA frame)
    #     ellipse_dims = self.c.get_ellipse_width_height()
    #     if not ellipse_dims:
    #         self.c.compute_ellipse_dimensions()
    #         ellipse_dims = self.c.get_ellipse_width_height()

    #     def monotone_chain_convex_hull(points):
    #         pts = sorted(points)
    #         if len(pts) <= 1:
    #             return pts

    #         def cross(o, a, b):
    #             return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    #         lower = []
    #         for p in pts:
    #             while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
    #                 lower.pop()
    #             lower.append(p)

    #         upper = []
    #         for p in reversed(pts):
    #             while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
    #                 upper.pop()
    #             upper.append(p)

    #         return lower[:-1] + upper[:-1]

    #     def sample_axis_aligned_ellipse(a, b, n):
    #         t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    #         ex = a * np.cos(t)
    #         ey = b * np.sin(t)
    #         return np.stack([ex, ey], axis=1)

    #     def chamfer_similarity(A, B, scale):
    #         from scipy.spatial.distance import cdist
    #         D = cdist(A, B)
    #         d_ab = np.mean(np.min(D, axis=1))
    #         d_ba = np.mean(np.min(D, axis=0))
    #         d = 0.5 * (d_ab + d_ba)
    #         return float(1.0 / (1.0 + (d / max(scale, 1e-9))))

        # for name, pts in coords_by_name.items():
        #     if not pts or len(pts) < 3:
        #         self.ellipse_similarity[name] = 0.0
        #         continue

        #     pts_np = np.asarray(pts, dtype=float)
        #     # Center for PCA (defensive in case upstream didn't center)
        #     centroid = pts_np.mean(axis=0)
        #     pts_centered = pts_np - centroid

        #     # PCA alignment so ellipse is axis-aligned in this frame
        #     from sklearn.decomposition import PCA
        #     pca = PCA(n_components=2)
        #     pca.fit(pts_centered)
        #     pts_rotated = pca.transform(pts_centered)

        #     # Use existing ellipse dims if available; else compute from rotated
        #     if name in ellipse_dims:
        #         width, height = ellipse_dims[name]
        #     else:
        #         width = float(np.max(pts_rotated[:, 0]) - np.min(pts_rotated[:, 0]))
        #         height = float(np.max(pts_rotated[:, 1]) - np.min(pts_rotated[:, 1]))

        #     a = 0.5 * width
        #     b = 0.5 * height
        #     ellipse_pts = sample_axis_aligned_ellipse(a, b, num_samples)

        #     # Figure boundary in the same rotated frame
        #     hull_rot = monotone_chain_convex_hull(pts_rotated.tolist())
        #     hull_rot = np.asarray(hull_rot, dtype=float)
        #     if hull_rot.shape[0] < 3:
        #         self.ellipse_similarity[name] = 0.0
        #         continue

        #     scale = max(a, b)
        #     similarity = round(chamfer_similarity(ellipse_pts, hull_rot, scale), 2)
        #     print(f"{name} similarity to an ellipse is: {similarity*100}%")
        #     self.ellipse_similarity[name] = similarity

    
    def get_shape_similarities(self):
        ellipse = self.c.get_ellipse_width_height()
        figure = self.c.get_coordinates()

        # Ensure we have coordinates and ellipse dimensions for THIS PLOT instance
        if not figure:
            self.c.read_file()
            self.c.to_array(center_at_origin=True)
            figure = self.c.get_coordinates()

        if not ellipse:
            self.c.compute_ellipse_dimensions()
            ellipse = self.c.get_ellipse_width_height()

        if not ellipse:
            print("Ellipse dimensions not available. Aborting shape similarity computation.")
            return

        def construct_ellipse(width, height, num_points, cx=0.0, cy=0.0):
            if num_points <= 0:
                return np.empty((0, 2), dtype=float)
            angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
            ellipse_points = np.column_stack((
                cx + (width / 2.0) * np.cos(angles),
                cy + (height / 2.0) * np.sin(angles)
            ))
            return ellipse_points
        
        def split_figure(coords):
            arr = np.asarray(coords, dtype=float)
            if arr.size == 0:
                return [], []
            pos_coords = arr[arr[:, 0] >= 0].tolist()
            neg_coords = arr[arr[:, 0] <= 0].tolist()
            return pos_coords, neg_coords

        for name, (width, height) in ellipse.items():
            pts = figure.get(name)
            if not pts:
                print(f"No coordinates for {name}, skipping...")
                continue
            num_points = len(pts)
            if num_points == 0:
                print(f"Empty coordinates for {name}, skipping...")
                continue


            pos_fig_pts, neg_fig_pts = split_figure(np.asarray(pts, dtype=float))
            num_pos = len(pos_fig_pts)
            num_neg = len(neg_fig_pts)

            pos_ellipse_pts = construct_ellipse(width, height, num_pos, cx=0.0, cy=0.0)
            neg_ellipse_pts = construct_ellipse(width, height, num_neg, cx=0.0, cy=0.0)
            
            pos_ellipse_pts = np.asarray(pos_ellipse_pts, dtype=float)
            neg_ellipse_pts = np.asarray(neg_ellipse_pts, dtype=float)
            pos_fig_pts = np.asarray(pos_fig_pts, dtype=float)
            neg_fig_pts = np.asarray(neg_fig_pts, dtype=float)

            pos_similarity = shape_similarity(pos_ellipse_pts, pos_fig_pts)
            neg_similarity = shape_similarity(neg_ellipse_pts, neg_fig_pts)
            similarity = round(100 * (pos_similarity + neg_similarity) / 2.0, 2)
            print(f"{name} similarity to an ellipse is: {similarity}%")
            self.ellipse_similarity[name] = similarity

        