import numpy as np
import os
import sys
from scipy.spatial.distance import cdist
from shapesimilarity import shape_similarity
import cv2
from plotting import PLOT
from shapes import SHAPE
from helper import HELPER

class COMPARE:
    def __init__(self, dxf_folder, BASE_DIR):
        self.BASE_DIR = BASE_DIR
        self.dxf_folder = dxf_folder
        self.shape = SHAPE()
        self.helper = HELPER()
        self.ellipse_areas = dict()
        self.ellipse_circumference = dict()
        self.diamond_areas = dict()
        self.rectangle_areas = dict()
        self.figure_areas = dict()
        self.figure_circumference = dict()
        self.ellipse_similarity = dict()
        self.diamond_similarity = dict()
        self.rectangle_similarity = dict()
        self.upper_h_ellipse_datapoints = dict()
        self.lower_h_ellipse_datapoints = dict()
        self.upper_h_diamond_datapoints = dict()
        self.lower_h_diamond_datapoints = dict()
        self.upper_h_figure_datapoints = dict()
        self.lower_h_figure_datapoints = dict()
        self.upper_v_ellipse_datapoints = dict()
        self.lower_v_ellipse_datapoints = dict()
        self.upper_v_diamond_datapoints = dict()
        self.lower_v_diamond_datapoints = dict()
        self.upper_v_figure_datapoints = dict()
        self.lower_v_figure_datapoints = dict()
        self.w_shape = 0.9
        self.w_area = 0.1
    
    def get_ellipse_similarities(self):
        return self.ellipse_similarity

    def get_diamond_similarities(self):
        return self.diamond_similarity
    
    def get_rectangle_similarities(self):
        return self.rectangle_similarity

    def get_upper_h_ellipse_datapoints(self):
        return self.upper_h_ellipse_datapoints
    
    def get_upper_h_diamond_datapoints(self):
        return self.upper_h_diamond_datapoints

    def get_upper_h_figure_datapoints(self):
        return self.upper_h_figure_datapoints

    def get_lower_h_ellipse_datapoints(self):
        return self.lower_h_ellipse_datapoints

    def get_lower_h_diamond_datapoints(self):
        return self.lower_h_diamond_datapoints

    def get_lower_h_figure_datapoints(self):
        return self.lower_h_figure_datapoints
    
    def get_upper_v_ellipse_datapoints(self):
        return self.upper_v_ellipse_datapoints
    
    def get_upper_v_diamond_datapoints(self):
        return self.upper_v_diamond_datapoints

    def get_upper_v_figure_datapoints(self):
        return self.upper_v_figure_datapoints

    def get_lower_v_ellipse_datapoints(self):
        return self.lower_v_ellipse_datapoints

    def get_lower_v_diamond_datapoints(self):
        return self.lower_v_diamond_datapoints

    def get_lower_v_figure_datapoints(self):
        return self.lower_v_figure_datapoints

    def get_ellipse_circumferences(self, plot):

        def circumference(a, b):
            h = (a-b)**2 / (a+b)**2
            c = np.pi*(a+b)*(1+(3*h)/10+np.sqrt(4-3*h))
            return c

        ellipse = plot.get_width_height()
        if not ellipse:
            if not plot.get_coordinates():
                plot.read_file()
                plot.to_array(center_at_origin=True)

            plot.compute_ellipse_dimensions()
            ellipse = plot.get_width_height()
        for name, (width, height) in ellipse.items():
            self.ellipse_circumference[name] = circumference(width/2, height/2)
    

    def get_ellipse_areas(self, plot):
        ellipse = plot.get_width_height()
        if not ellipse:
            if not plot.get_coordinates():
                plot.read_file()
                plot.to_array(center_at_origin=True)

            plot.compute_dimensions()
            ellipse = plot.get_width_height()
        for name, (width, height) in ellipse.items():
            self.ellipse_areas[name] = float(np.pi * (width * 0.5) * (height * 0.5))


    def get_diamond_areas(self, plot):
        diamond = plot.get_width_height()
        if not diamond:
            if not plot.get_coordinates():
                plot.read_file()
                plot.to_array(center_at_origin=True)

            plot.compute_dimensions()
            diamond = plot.get_width_height()
        for name, (width, height) in diamond.items():
            self.diamond_areas[name] = float(0.5 * width * height)


    def get_figure_areas(self, plot):
        coords_by_name = plot.get_coordinates()
        if not coords_by_name:
            print("coords not found")
            plot.read_file()
            plot.to_array(center_at_origin=False)
            coords_by_name = plot.get_coordinates()

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
        return self.figure_areas


    def get_figure_circumferences(self, plot):
        coords_by_name = plot.get_coordinates()
        if not coords_by_name:
            plot.read_file()
            plot.to_array(center_at_origin=False)
            coords_by_name = plot.get_coordinates()

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
        return self.figure_circumference

    def get_rectangle_areas(self, plot):
        rectangle = plot.get_width_height()
        if not rectangle:
            if not plot.get_coordinates():
                plot.read_file()
                plot.to_array(center_at_origin=True)

            plot.compute_dimensions()
            rectangle = plot.get_width_height()
        for name, (width, height) in rectangle.items():
            self.rectangle_areas[name] = float(width * height)


    def compare_circumferences(self):
        for name, circumference in self.ellipse_circumference.items():
            difference = self.figure_circumference[name] / circumference
            precentage = 100 * difference
            print(f"{name} is {precentage}% ellipse")
    


    def compare_ellipse_areas(self):
        compared_ellipse_areas = dict()
        for name, area in self.ellipse_areas.items():
            difference = self.figure_areas[name] / area
            compared_ellipse_areas[name] = difference
        return compared_ellipse_areas
        

    def compare_diamond_areas(self):
        compared_diamond_areas = dict()
        for name, area in self.diamond_areas.items():
            difference = self.figure_areas[name] / area
            compared_diamond_areas[name] = difference
        return compared_diamond_areas
    

    def compare_rectangle_areas(self):
        compared_rectangle_areas = dict()
        for name, area in self.rectangle_areas.items():
            difference = self.figure_areas[name] / area
            compared_rectangle_areas[name] = difference
        return compared_rectangle_areas



    def calculate_dynamic_ellipse_similarity(self, ellipse, figure, compared_areas):
        for name, (width, height) in ellipse.items():
            pts = figure.get(name)
            if not pts:
                print(f"No coordinates for {name}, skipping...")
                continue
            num_points = len(pts)
            if num_points == 0:
                print(f"Empty coordinates for {name}, skipping...")
                continue

            pos_h_fig_pts, neg_h_fig_pts = self.shape.split_figure_horizontally(np.asarray(pts, dtype=float))
            pos_v_fig_pts, neg_v_fig_pts = self.shape.split_figure_vertically(np.asarray(pts, dtype=float))
            n_top = len(pos_h_fig_pts)
            n_bottom = len(neg_h_fig_pts)
            n_right = len(pos_v_fig_pts)
            n_left = len(neg_v_fig_pts)
            # Skip if either half is empty
            if min(n_top, n_bottom, n_right, n_left) < 2:
                print(f"Insufficient points in one half for {name}, skipping...")
                continue

            # Construct horizontal half-ellipses with matching point counts
            pos_h_ellipse_pts = self.shape.construct_half_ellipse_horizontal(width, height, n_top, side='pos', cx=0.0, cy=0.0)
            neg_h_ellipse_pts = self.shape.construct_half_ellipse_horizontal(width, height, n_bottom, side='neg', cx=0.0, cy=0.0)

            pos_h_ellipse_pts = np.asarray(pos_h_ellipse_pts, dtype=float)
            neg_h_ellipse_pts = np.asarray(neg_h_ellipse_pts, dtype=float)
            self.upper_h_ellipse_datapoints[name] = pos_h_ellipse_pts
            self.lower_h_ellipse_datapoints[name] = neg_h_ellipse_pts

            pos_h_fig_pts = np.asarray(pos_h_fig_pts, dtype=float)
            neg_h_fig_pts = np.asarray(neg_h_fig_pts, dtype=float)
            self.upper_h_figure_datapoints[name] = pos_h_fig_pts
            self.lower_h_figure_datapoints[name] = neg_h_fig_pts

            pos_h_similarity = self.helper.raw_shape_similarity(pos_h_ellipse_pts, pos_h_fig_pts)
            neg_h_similarity = self.helper.raw_shape_similarity(neg_h_ellipse_pts, neg_h_fig_pts)

            # Construct vertical half-ellipses with matching point counts
            pos_v_ellipse_pts = self.shape.construct_half_ellipse_vertical(width, height, n_right, side='pos', cx=0.0, cy=0.0)
            neg_v_ellipse_pts = self.shape.construct_half_ellipse_vertical(width, height, n_left, side='neg', cx=0.0, cy=0.0)

            pos_v_ellipse_pts = np.asarray(pos_v_ellipse_pts, dtype=float)
            neg_v_ellipse_pts = np.asarray(neg_v_ellipse_pts, dtype=float)
            self.upper_v_ellipse_datapoints[name] = pos_v_ellipse_pts
            self.lower_v_ellipse_datapoints[name] = neg_v_ellipse_pts

            pos_v_fig_pts = np.asarray(pos_v_fig_pts, dtype=float)
            neg_v_fig_pts = np.asarray(neg_v_fig_pts, dtype=float)
            self.upper_v_figure_datapoints[name] = pos_v_fig_pts
            self.lower_v_figure_datapoints[name] = neg_v_fig_pts

            pos_v_similarity = self.helper.raw_shape_similarity(pos_v_ellipse_pts, pos_v_fig_pts)
            neg_v_similarity = self.helper.raw_shape_similarity(neg_v_ellipse_pts, neg_v_fig_pts)

            similarity = round(100*(pos_h_similarity + neg_h_similarity + pos_v_similarity + neg_v_similarity) / 4.0, 2)

            # Add area comparison to the formula
            combined_similarities = round(self.w_shape * similarity + self.w_area * compared_areas[name], 2)
            print(f"{name} similarity to an ellipse is: {combined_similarities}%")

            self.ellipse_similarity[name] = combined_similarities
    


    def calculate_static_ellipse_similarity(self, width, height, figure, compared_areas):
        for name, pts in figure.items():
            if not pts:
                print(f"No coordinates for {name}, skipping...")
                continue
            num_points = len(pts)
            if num_points == 0:
                print(f"Empty coordinates for {name}, skipping...")
                continue

            pos_h_fig_pts, neg_h_fig_pts = self.shape.split_figure_horizontally(np.asarray(pts, dtype=float))
            pos_v_fig_pts, neg_v_fig_pts = self.shape.split_figure_vertically(np.asarray(pts, dtype=float))
            n_top = len(pos_h_fig_pts)
            n_bottom = len(neg_h_fig_pts)
            n_right = len(pos_v_fig_pts)
            n_left = len(neg_v_fig_pts)

            # Skip if either half is empty
            if min(n_top, n_bottom, n_right, n_left) < 2:
                print(f"Insufficient points in one half for {name}, skipping...")
                continue
            # Construct half-ellipses with matching point counts using static dimensions
            pos_h_ellipse_pts = self.shape.construct_half_ellipse_horizontal(width, height, n_top, side='pos', cx=0.0, cy=0.0)
            neg_h_ellipse_pts = self.shape.construct_half_ellipse_horizontal(width, height, n_bottom, side='neg', cx=0.0, cy=0.0)

            pos_h_ellipse_pts = np.asarray(pos_h_ellipse_pts, dtype=float)
            neg_h_ellipse_pts = np.asarray(neg_h_ellipse_pts, dtype=float)
            self.upper_h_ellipse_datapoints[name] = pos_h_ellipse_pts
            self.lower_h_ellipse_datapoints[name] = neg_h_ellipse_pts

            pos_h_fig_pts = np.asarray(pos_h_fig_pts, dtype=float)
            neg_h_fig_pts = np.asarray(neg_h_fig_pts, dtype=float)
            self.upper_h_figure_datapoints[name] = pos_h_fig_pts
            self.lower_h_figure_datapoints[name] = neg_h_fig_pts

            pos_h_similarity = self.helper.raw_shape_similarity(pos_h_ellipse_pts, pos_h_fig_pts)
            neg_h_similarity = self.helper.raw_shape_similarity(neg_h_ellipse_pts, neg_h_fig_pts)

            pos_v_ellipse_pts = self.shape.construct_half_ellipse_vertical(width, height, n_right, side='pos', cx=0.0, cy=0.0)
            neg_v_ellipse_pts = self.shape.construct_half_ellipse_vertical(width, height, n_left, side='neg', cx=0.0, cy=0.0)

            pos_v_ellipse_pts = np.asarray(pos_v_ellipse_pts, dtype=float)
            neg_v_ellipse_pts = np.asarray(neg_v_ellipse_pts, dtype=float)
            self.upper_v_ellipse_datapoints[name] = pos_v_ellipse_pts
            self.lower_v_ellipse_datapoints[name] = neg_v_ellipse_pts

            pos_v_fig_pts = np.asarray(pos_v_fig_pts, dtype=float)
            neg_v_fig_pts = np.asarray(neg_v_fig_pts, dtype=float)
            self.upper_v_figure_datapoints[name] = pos_v_fig_pts
            self.lower_v_figure_datapoints[name] = neg_v_fig_pts

            pos_v_similarity = self.helper.raw_shape_similarity(pos_v_ellipse_pts, pos_v_fig_pts)
            neg_v_similarity = self.helper.raw_shape_similarity(neg_v_ellipse_pts, neg_v_fig_pts)

            similarity = round(100*(pos_h_similarity + neg_h_similarity + pos_v_similarity + neg_v_similarity) / 4.0, 2)

            # Add area comparison to the formula
            combined_similarities = round(self.w_shape * similarity + self.w_area * compared_areas[name], 2)

            print(f"{name} similarity to static ellipse is: {combined_similarities}%")
            self.ellipse_similarity[name] = combined_similarities


    def calculate_dynamic_diamond_similarity(self, diamond, figure, compared_areas):
        for name, (width, height) in diamond.items():
            pts = figure.get(name)
            if not pts:
                print(f"No coordinates for {name}, skipping...")
                continue
            num_points = len(pts)
            if num_points == 0:
                print(f"Empty coordinates for {name}, skipping...")
                continue

            pos_h_fig_pts, neg_h_fig_pts = self.shape.split_figure_horizontally(np.asarray(pts, dtype=float))
            pos_v_fig_pts, neg_v_fig_pts = self.shape.split_figure_vertically(np.asarray(pts, dtype=float))
            n_top = len(pos_h_fig_pts)
            n_bottom = len(neg_h_fig_pts)
            n_right = len(pos_v_fig_pts)
            n_left = len(neg_v_fig_pts)

            # Skip if either half is empty
            if min(n_top, n_bottom, n_right, n_left) < 2:
                print(f"Insufficient points in one half for {name}, skipping...")
                continue

            # Construct half-diamonds with matching point counts
            pos_h_diamond_pts = self.shape.construct_half_diamond_horizontal(width, height, n_top, side='pos', cx=0.0, cy=0.0)
            neg_h_diamond_pts = self.shape.construct_half_diamond_horizontal(width, height, n_bottom, side='neg', cx=0.0, cy=0.0)

            pos_h_diamond_pts = np.asarray(pos_h_diamond_pts, dtype=float)
            neg_h_diamond_pts = np.asarray(neg_h_diamond_pts, dtype=float)
            self.upper_h_diamond_datapoints[name] = pos_h_diamond_pts
            self.lower_h_diamond_datapoints[name] = neg_h_diamond_pts

            pos_h_fig_pts = np.asarray(pos_h_fig_pts, dtype=float)
            neg_h_fig_pts = np.asarray(neg_h_fig_pts, dtype=float)
            self.upper_h_figure_datapoints[name] = pos_h_fig_pts
            self.lower_h_figure_datapoints[name] = neg_h_fig_pts

            pos_h_similarity = self.helper.raw_shape_similarity(pos_h_diamond_pts, pos_h_fig_pts)
            neg_h_similarity = self.helper.raw_shape_similarity(neg_h_diamond_pts, neg_h_fig_pts)

            # Construct vertical half-diamonds with matching point counts
            pos_v_diamond_pts = self.shape.construct_half_diamond_vertical(width, height, n_right, side='pos', cx=0.0, cy=0.0)
            neg_v_diamond_pts = self.shape.construct_half_diamond_vertical(width, height, n_left, side='neg', cx=0.0, cy=0.0)

            pos_v_diamond_pts = np.asarray(pos_v_diamond_pts, dtype=float)
            neg_v_diamond_pts = np.asarray(neg_v_diamond_pts, dtype=float)
            self.upper_v_diamond_datapoints[name] = pos_v_diamond_pts
            self.lower_v_diamond_datapoints[name] = neg_v_diamond_pts

            pos_v_fig_pts = np.asarray(pos_v_fig_pts, dtype=float)
            neg_v_fig_pts = np.asarray(neg_v_fig_pts, dtype=float)
            self.upper_v_figure_datapoints[name] = pos_v_fig_pts
            self.lower_v_figure_datapoints[name] = neg_v_fig_pts

            pos_v_similarity = self.helper.raw_shape_similarity(pos_v_diamond_pts, pos_v_fig_pts)
            neg_v_similarity = self.helper.raw_shape_similarity(neg_v_diamond_pts, neg_v_fig_pts)

            similarity = round(100 * (pos_h_similarity + neg_h_similarity + pos_v_similarity + neg_v_similarity) / 4.0, 2)
            
            # Add area comparison to the formula
            combined_similarities = round(self.w_shape * similarity + self.w_area * compared_areas[name], 2)

            print(f"{name} similarity to a diamond is: {combined_similarities}%")
            self.diamond_similarity[name] = combined_similarities



    def calculate_static_diamond_similarity(self, width, height, figure, compared_areas):
        for name, pts in figure.items():
            if not pts:
                print(f"No coordinates for {name}, skipping...")
                continue
            num_points = len(pts)
            if num_points == 0:
                print(f"Empty coordinates for {name}, skipping...")
                continue

            pos_h_fig_pts, neg_h_fig_pts = self.shape.split_figure_horizontally(np.asarray(pts, dtype=float))
            pos_v_fig_pts, neg_v_fig_pts = self.shape.split_figure_vertically(np.asarray(pts, dtype=float))
            n_top = len(pos_h_fig_pts)
            n_bottom = len(neg_h_fig_pts)
            n_right = len(pos_v_fig_pts)
            n_left = len(neg_v_fig_pts)

            # Skip if either half is empty
            if min(n_top, n_bottom, n_right, n_left) < 2:
                print(f"Insufficient points in one half for {name}, skipping...")
                continue

            # Construct half-diamonds with matching point counts using static dimensions
            pos_h_diamond_pts = self.shape.construct_half_diamond_horizontal(width, height, n_top, side='pos', cx=0.0, cy=0.0)
            neg_h_diamond_pts = self.shape.construct_half_diamond_horizontal(width, height, n_bottom, side='neg', cx=0.0, cy=0.0)

            pos_h_diamond_pts = np.asarray(pos_h_diamond_pts, dtype=float)
            neg_h_diamond_pts = np.asarray(neg_h_diamond_pts, dtype=float)
            self.upper_h_diamond_datapoints[name] = pos_h_diamond_pts
            self.lower_h_diamond_datapoints[name] = neg_h_diamond_pts

            pos_h_fig_pts = np.asarray(pos_h_fig_pts, dtype=float)
            neg_h_fig_pts = np.asarray(neg_h_fig_pts, dtype=float)
            self.upper_h_figure_datapoints[name] = pos_h_fig_pts
            self.lower_h_figure_datapoints[name] = neg_h_fig_pts

            pos_h_similarity = self.helper.raw_shape_similarity(pos_h_diamond_pts, pos_h_fig_pts)
            neg_h_similarity = self.helper.raw_shape_similarity(neg_h_diamond_pts, neg_h_fig_pts)

            # Construct vertical half-diamonds with matching point counts using static dimensions
            pos_v_diamond_pts = self.shape.construct_half_diamond_vertical(width, height, n_right, side='pos', cx=0.0, cy=0.0)
            neg_v_diamond_pts = self.shape.construct_half_diamond_vertical(width, height, n_left, side='neg', cx=0.0, cy=0.0)

            pos_v_diamond_pts = np.asarray(pos_v_diamond_pts, dtype=float)
            neg_v_diamond_pts = np.asarray(neg_v_diamond_pts, dtype=float)
            self.upper_v_diamond_datapoints[name] = pos_v_diamond_pts
            self.lower_v_diamond_datapoints[name] = neg_v_diamond_pts

            pos_v_fig_pts = np.asarray(pos_v_fig_pts, dtype=float)
            neg_v_fig_pts = np.asarray(neg_v_fig_pts, dtype=float)
            self.upper_v_figure_datapoints[name] = pos_v_fig_pts
            self.lower_v_figure_datapoints[name] = neg_v_fig_pts

            pos_v_similarity = self.helper.raw_shape_similarity(pos_v_diamond_pts, pos_v_fig_pts)
            neg_v_similarity = self.helper.raw_shape_similarity(neg_v_diamond_pts, neg_v_fig_pts)

            similarity = round(100 * (pos_h_similarity + neg_h_similarity + pos_v_similarity + neg_v_similarity) / 4.0, 2)
            
            # Add area comparison to the formula
            combined_similarities = round(self.w_shape * similarity + self.w_area * compared_areas[name], 2)

            print(f"{name} similarity to static diamond is: {combined_similarities}%")
            self.diamond_similarity[name] = combined_similarities



    def calculate_dynamic_rectangle_similarity(self, rectangle, figure, compared_areas):
        for name, (width, height) in rectangle.items():
            pts = figure.get(name)
            if not pts:
                print(f"No coordinates for {name}, skipping...")
                continue
            num_points = len(pts)
            if num_points == 0:
                print(f"Empty coordinates for {name}, skipping...")
                continue

            pos_h_fig_pts, neg_h_fig_pts = self.shape.split_figure_horizontally(np.asarray(pts, dtype=float))
            pos_v_fig_pts, neg_v_fig_pts = self.shape.split_figure_vertically(np.asarray(pts, dtype=float))
            n_top = len(pos_h_fig_pts)
            n_bottom = len(neg_h_fig_pts)
            n_right = len(pos_v_fig_pts)
            n_left = len(neg_v_fig_pts)

            if min(n_top, n_bottom, n_right, n_left) < 2:
                print(f"Insufficient points in one half for {name}, skipping...")
                continue

            pos_h_rect_pts = self.shape.construct_half_rectangle_horizontal(width, height, n_top, side='pos', cx=0.0, cy=0.0)
            neg_h_rect_pts = self.shape.construct_half_rectangle_horizontal(width, height, n_bottom, side='neg', cx=0.0, cy=0.0)

            pos_h_rect_pts = np.asarray(pos_h_rect_pts, dtype=float)
            neg_h_rect_pts = np.asarray(neg_h_rect_pts, dtype=float)

            pos_h_fig_pts = np.asarray(pos_h_fig_pts, dtype=float)
            neg_h_fig_pts = np.asarray(neg_h_fig_pts, dtype=float)

            pos_h_similarity = self.helper.raw_shape_similarity(pos_h_rect_pts, pos_h_fig_pts)
            neg_h_similarity = self.helper.raw_shape_similarity(neg_h_rect_pts, neg_h_fig_pts)

            pos_v_rect_pts = self.shape.construct_half_rectangle_vertical(width, height, n_right, side='pos', cx=0.0, cy=0.0)
            neg_v_rect_pts = self.shape.construct_half_rectangle_vertical(width, height, n_left, side='neg', cx=0.0, cy=0.0)

            pos_v_rect_pts = np.asarray(pos_v_rect_pts, dtype=float)
            neg_v_rect_pts = np.asarray(neg_v_rect_pts, dtype=float)

            pos_v_fig_pts = np.asarray(pos_v_fig_pts, dtype=float)
            neg_v_fig_pts = np.asarray(neg_v_fig_pts, dtype=float)

            pos_v_similarity = self.helper.raw_shape_similarity(pos_v_rect_pts, pos_v_fig_pts)
            neg_v_similarity = self.helper.raw_shape_similarity(neg_v_rect_pts, neg_v_fig_pts)

            similarity = round(100 * (pos_h_similarity + neg_h_similarity + pos_v_similarity + neg_v_similarity) / 4.0, 2)
            
            combined_similarities = round(self.w_shape * similarity + self.w_area * compared_areas[name], 2)
            print(f"{name} similarity to a rectangle is: {combined_similarities}%")

            self.rectangle_similarity[name] = combined_similarities



    def calculate_static_rectangle_similarity(self, width, height, figure, compared_areas):
        for name, pts in figure.items():
            if not pts:
                print(f"No coordinates for {name}, skipping...")
                continue
            num_points = len(pts)
            if num_points == 0:
                print(f"Empty coordinates for {name}, skipping...")
                continue

            pos_h_fig_pts, neg_h_fig_pts = self.shape.split_figure_horizontally(np.asarray(pts, dtype=float))
            pos_v_fig_pts, neg_v_fig_pts = self.shape.split_figure_vertically(np.asarray(pts, dtype=float))
            n_top = len(pos_h_fig_pts)
            n_bottom = len(neg_h_fig_pts)
            n_right = len(pos_v_fig_pts)
            n_left = len(neg_v_fig_pts)

            if min(n_top, n_bottom, n_right, n_left) < 2:
                print(f"Insufficient points in one half for {name}, skipping...")
                continue

            pos_h_rect_pts = self.shape.construct_half_rectangle_horizontal(width, height, n_top, side='pos', cx=0.0, cy=0.0)
            neg_h_rect_pts = self.shape.construct_half_rectangle_horizontal(width, height, n_bottom, side='neg', cx=0.0, cy=0.0)

            pos_h_rect_pts = np.asarray(pos_h_rect_pts, dtype=float)
            neg_h_rect_pts = np.asarray(neg_h_rect_pts, dtype=float)

            pos_h_fig_pts = np.asarray(pos_h_fig_pts, dtype=float)
            neg_h_fig_pts = np.asarray(neg_h_fig_pts, dtype=float)

            pos_h_similarity = self.helper.raw_shape_similarity(pos_h_rect_pts, pos_h_fig_pts)
            neg_h_similarity = self.helper.raw_shape_similarity(neg_h_rect_pts, neg_h_fig_pts)

            pos_v_rect_pts = self.shape.construct_half_rectangle_vertical(width, height, n_right, side='pos', cx=0.0, cy=0.0)
            neg_v_rect_pts = self.shape.construct_half_rectangle_vertical(width, height, n_left, side='neg', cx=0.0, cy=0.0)

            pos_v_rect_pts = np.asarray(pos_v_rect_pts, dtype=float)
            neg_v_rect_pts = np.asarray(neg_v_rect_pts, dtype=float)

            pos_v_fig_pts = np.asarray(pos_v_fig_pts, dtype=float)
            neg_v_fig_pts = np.asarray(neg_v_fig_pts, dtype=float)

            pos_v_similarity = self.helper.raw_shape_similarity(pos_v_rect_pts, pos_v_fig_pts)
            neg_v_similarity = self.helper.raw_shape_similarity(neg_v_rect_pts, neg_v_fig_pts)

            similarity = round(100 * (pos_h_similarity + neg_h_similarity + pos_v_similarity + neg_v_similarity) / 4.0, 2)
            
            combined_similarities = round(self.w_shape * similarity + self.w_area * compared_areas[name], 2)
            print(f"{name} similarity to static rectangle is: {combined_similarities}%")

            self.rectangle_similarity[name] = combined_similarities



    def get_ellipse_shape_similarities(self, plot, typ="dynamic"):
        self.ellipse_similarity = {}
        compared_ellipse_areas = self.compare_ellipse_areas()
        if typ == "dynamic":
            ellipse = plot.get_width_height()
            figure = plot.get_coordinates()

            # Ensure we have coordinates and ellipse dimensions for THIS PLOT instance
            if not figure:
                plot.read_file()
                plot.to_array(center_at_origin=True)
                figure = plot.get_coordinates()

            if not ellipse:
                plot.compute_dimensions()
                ellipse = plot.get_width_height()
        
            if not ellipse:
                print("Ellipse dimensions not available. Aborting shape similarity computation.")
                return
            
            self.calculate_dynamic_ellipse_similarity(ellipse, figure, compared_ellipse_areas)

        elif typ == "static":
            figure = plot.get_coordinates()
            
            # Ensure we have coordinates
            if not figure:
                plot.read_file()
                plot.to_array(center_at_origin=True)
                figure = plot.get_coordinates()
            
            # Ensure we have average width/height computed
            avg_w_h = plot.get_average_width_height()
            if not avg_w_h or len(avg_w_h) < 2:
                # Need to compute dimensions first, then average
                if not plot.get_width_height():
                    plot.compute_dimensions()
                plot.take_average_width_height()
                avg_w_h = plot.get_average_width_height()
            
            if not avg_w_h or len(avg_w_h) < 2:
                print("Average width/height not available. Aborting shape similarity computation.")
                return
            
            width = avg_w_h[0]
            height = avg_w_h[1]
        
            print(f"Using static ellipse dimensions: width={width}, height={height}")
            
            self.calculate_static_ellipse_similarity(width, height, figure, compared_ellipse_areas)
            
    


    def get_diamond_shape_similarities(self, plot, typ="dynamic"):
        self.diamond_similarity = {}
        compared_diamond_areas = self.compare_diamond_areas()
        if typ == "dynamic":
            diamond = plot.get_width_height()
            figure = plot.get_coordinates()

            # Ensure we have coordinates and diamond dimensions for THIS PLOT instance
            if not figure:
                plot.read_file()
                plot.to_array(center_at_origin=True)
                figure = plot.get_coordinates()

            if not diamond:
                plot.compute_dimensions()
                diamond = plot.get_width_height()

            if not diamond:
                print("Diamond dimensions not available. Aborting shape similarity computation.")
                return

            self.calculate_dynamic_diamond_similarity(diamond, figure, compared_diamond_areas)

        elif typ == "static":
            figure = plot.get_coordinates()
            
            # Ensure we have coordinates
            if not figure:
                plot.read_file()
                plot.to_array(center_at_origin=True)
                figure = plot.get_coordinates()
            
            # Ensure we have average width/height computed
            avg_w_h = plot.get_average_width_height()
            if not avg_w_h or len(avg_w_h) < 2:
                # Need to compute dimensions first, then average
                if not plot.get_width_height():
                    plot.compute_dimensions()
                plot.take_average_width_height()
                avg_w_h = plot.get_average_width_height()
            
            if not avg_w_h or len(avg_w_h) < 2:
                print("Average width/height not available. Aborting shape similarity computation.")
                return
            
            width = avg_w_h[0]
            height = avg_w_h[1]
            print(f"Using static diamond dimensions: width={width}, height={height}")
            
            self.calculate_static_diamond_similarity(width, height, figure, compared_diamond_areas)



    def get_rectangle_shape_similarities(self, plot, typ="dynamic"):
        self.rectangle_similarity = {}
        compared_rectangle_areas = self.compare_rectangle_areas()
        if typ == "dynamic":
            rectangle = plot.get_width_height()
            figure = plot.get_coordinates()

            if not figure:
                plot.read_file()
                plot.to_array(center_at_origin=True)
                figure = plot.get_coordinates()

            if not rectangle:
                plot.compute_dimensions()
                rectangle = plot.get_width_height()

            if not rectangle:
                print("Rectangle dimensions not available. Aborting shape similarity computation.")
                return

            self.calculate_dynamic_rectangle_similarity(rectangle, figure, compared_rectangle_areas)

        elif typ == "static":
            figure = plot.get_coordinates()
            
            if not figure:
                plot.read_file()
                plot.to_array(center_at_origin=True)
                figure = plot.get_coordinates()
            
            avg_w_h = plot.get_average_width_height()
            if not avg_w_h or len(avg_w_h) < 2:
                if not plot.get_width_height():
                    plot.compute_dimensions()
                plot.take_average_width_height()
                avg_w_h = plot.get_average_width_height()
            
            if not avg_w_h or len(avg_w_h) < 2:
                print("Average width/height not available. Aborting shape similarity computation.")
                return
            
            width = avg_w_h[0]
            height = avg_w_h[1]
            print(f"Using static rectangle dimensions: width={width}, height={height}")
            
            self.calculate_static_rectangle_similarity(width, height, figure, compared_rectangle_areas)