import matplotlib.pyplot as plt
from helper import HELPER
import numpy as np
import ezdxf as dxf
import os
import sys
from matplotlib.patches import Ellipse, Polygon

class PLOT:
    def __init__(self, dxf_path, BASE_DIR):
        self.BASE_DIR = BASE_DIR
        self.dxf_path = dxf_path
        self.doc = None
        self.x_files = [entry for entry in os.listdir(self.dxf_path) if os.path.isfile(os.path.join(self.dxf_path, entry))]
        self.files = []
        self.width_height = dict()
        self.width_height_mean = list()
        self.coordinates = dict()
        self.img_folder = os.path.join(self.BASE_DIR, "plot_figures")
        self.helper = HELPER()

    def get_width_height(self):
        return self.width_height

    def get_coordinates(self):
        return self.coordinates

    def get_average_width_height(self):
        return self.width_height_mean

    def read_file(self, to_print=False):
        for i in self.x_files:
            try:
                self.doc = dxf.readfile(os.path.join(self.dxf_path, i))
                if to_print == True:
                    print(f"Found file {i}")
                self.files.append(self.doc)
            except IOError:
                print(f"Not a DXF file or a generic I/O error.")
                sys.exit(1)
            except dxf.DXFStructureError:
                print(f"Invalid or corrupted DXF file.")
                sys.exit(2)


    def to_array(self, center_at_origin=True):
        for i, doc in enumerate(self.files):
            coords = []
            msp = doc.modelspace()
            for entity in msp:
                if entity.dxftype() == "LINE":
                    coords.append([entity.dxf.start.x, entity.dxf.start.y])
                    coords.append([entity.dxf.end.x, entity.dxf.end.y])
                elif entity.dxftype() == "POINT":
                    coords.append([entity.dxf.location.x, entity.dxf.location.y])
                elif entity.dxftype() in ("LWPOLYLINE", "POLYLINE"):
                    for v in entity.get_points():
                        coords.append([v[0], v[1]])

            if center_at_origin and coords:
                coords = np.array(coords)
                # Calculate the centroid (mean of all points)
                centroid = np.mean(coords, axis=0)
                # Subtract centroid from all points to center at (0, 0)
                coords = coords - centroid
                coords = coords.tolist()

            coords = self.helper.sort_points_clockwise(coords)
            coords.append(coords[0])
            self.coordinates[f"Needle {i+1} ({self.x_files[i]})"] = coords


    def compute_dimensions(self):
        # Compute width/height after PCA rotation without plotting
        if not self.coordinates:
            return
        for name, coords in self.coordinates.items():
            if not coords:
                continue
            coords_np = np.array(coords)
            rotated = self.helper._rotate_coords_pca(coords_np)
            max_x = np.max(rotated[:, 0])
            min_x = np.min(rotated[:, 0])
            max_y = np.max(rotated[:, 1])
            min_y = np.min(rotated[:, 1])
            fig_width = max_x - min_x
            fig_length = max_y - min_y
            self.width_height[name] = (fig_width, fig_length)



    def take_average_width_height(self):
        dimensions = self.get_width_height()
        if not dimensions:
            if not self.get_coordinates():
                self.read_file()
                self.to_array()
            self.compute_dimensions()
            dimensions = self.get_width_height()

        width_height = np.array(list(dimensions.values()))
        width_mean = np.mean(width_height[:, 0])
        height_mean = np.mean(width_height[:, 1])
        self.width_height_mean = [width_mean, height_mean]



    def plot_similarity_dict_figures(self, datapoints, typ="dynamic", shape="ellipse", save=True, show=False):

        for name, coords in self.coordinates.items():
            if not coords:
                print(f"No coordinates found for {name}, skipping...")
                continue

            coords = np.array(coords)
            rotated_coords = self.helper._rotate_coords_pca(coords)

            figure, axes = plt.subplots(figsize=(12, 9))

            axes.plot(rotated_coords[:, 0], rotated_coords[:, 1], "bo-", label="DXF data")

            axes.plot(0, 0, 'r+', markersize=10, markeredgewidth=2, label="Origin (0,0)")

            
            if typ == "dynamic":
                fig_width = max(rotated_coords[:, 0]) - min(rotated_coords[:, 0]) # x-axis max ja min points absolute difference
                fig_length = max(rotated_coords[:, 1]) - min(rotated_coords[:, 1]) # y-axis max ja min points absolute difference
                self.width_height[name] = (fig_width, fig_length)
            elif typ == "static":
                (fig_width, fig_length) = self.get_average_width_height()

            if shape == "ellipse":
                ellipse = Ellipse( (0, 0), fig_width, fig_length, fill = False, linestyle="--", label="Reference circle")
                axes.add_patch(ellipse)
            elif shape == "diamond":
                diamond_points = [
                    (0, fig_length / 2.0),
                    (fig_width / 2.0, 0),
                    (0, -fig_length / 2.0),
                    (-fig_width / 2.0, 0),
                ]
                diamond = Polygon(
                    diamond_points,
                    closed=True,
                    fill=False,
                    linestyle="--",
                    edgecolor="red",
                    label="Reference diamond"
                )
                axes.add_patch(diamond)
            elif shape == "rectangle":
                rect_points = [
                    (-fig_width / 2.0, fig_length / 2.0),
                    (fig_width / 2.0, fig_length / 2.0),
                    (fig_width / 2.0, -fig_length / 2.0),
                    (-fig_width / 2.0, -fig_length / 2.0),
                ]
                rectangle = Polygon(
                        rect_points,
                        closed=True,
                        fill=False,
                        linestyle="--",
                        edgecolor="green",
                        label="Reference rectangle"
                    )
                axes.add_patch(rectangle)


            axes.text(0.05, 0, f"Similarity {datapoints[name]:.2f}%", backgroundcolor="blue", color="white", fontsize=16)

            axes.set_aspect("equal", adjustable="box")
            axes.set_title(f"Plot for {name}")
            axes.legend()
            axes.grid(True, alpha=0.3)

            axes.set_xlabel("X (mm)")
            axes.set_ylabel("Y (mm)")

            if save:
                figure.savefig(os.path.join(self.img_folder, f"{name}({typ} {shape}).png"), dpi=300)
                print(f"SAVED {name}{shape}.png")

            if show:
                plt.show()
            plt.close(figure)

    
        



    def plot_datapoint_dict_figures(self, datapoints, shape="figure", save=False, show=True):
        if len(datapoints) == 0:
            print(f"No data available!")
            return
        for name, coords in datapoints.items():
            if not list(coords):
                print(f"No coordinates found for {name}, skipping...")
                continue

            coords = np.array(coords)

            figure, axes = plt.subplots(figsize=(12, 9))

            axes.plot(coords[:, 0], coords[:, 1], "bo-", label="DXF data")

            axes.plot(0, 0, 'r+', markersize=10, markeredgewidth=2, label="Origin (0,0)")

            axes.set_aspect("equal", adjustable="box")
            axes.set_title(f"Plot for {name}")
            axes.legend()
            axes.grid(True, alpha=0.3)

            axes.set_xlabel("X (mm)")
            axes.set_ylabel("Y (mm)")

            if save:
                figure.savefig(os.path.join(self.img_folder, f"half_{name}({shape}).png"), dpi=300)
                print(f"SAVED {name}{shape}.png")

            if show:
                plt.show()
            plt.close(figure)

    
    def plot_list(self, datapoints, save=False, show=True):
        # Convert to numpy array first
        datapoints = np.asarray(datapoints, dtype=float)
        
        # Check if empty after conversion
        if datapoints.size == 0 or len(datapoints) == 0:
            print("There are no datapoints in this list!")
            return
        
        # Check if it's a 2D array with at least 2 columns (x, y)
        if datapoints.ndim != 2 or datapoints.shape[1] < 2:
            print(f"Expected 2D array with shape (n, 2), got shape {datapoints.shape}")
            return

        figure = plt.figure(figsize=(12, 8))
        # Plot all x and y coordinates: datapoints[:, 0] gets all x values, datapoints[:, 1] gets all y values
        plt.plot(datapoints[:, 0], datapoints[:, 1], "ro-", label="Half of the figure", linewidth=2, markersize=4)
        plt.title("Plot of datapoints")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xlabel("X (mm)")
        plt.ylabel("Y (mm)")
        plt.axis("equal")
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        plt.axvline(x=0, color='k', linestyle='--', alpha=0.3)

        if save:
            name = input("Give this shit a name: ")
            figure.savefig(os.path.join(self.img_folder, f"{name}.png"), dpi=300)
            print(f"SAVED {name}.png")

        if show:
            plt.show()
        else:
            plt.close(figure)
    




    