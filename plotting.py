import matplotlib.pyplot as plt
import numpy as np
import ezdxf as dxf
import os
import sys
from sklearn.decomposition import PCA
from matplotlib.patches import Ellipse

class PLOT:
    def __init__(self, dxf_path, BASE_DIR):
        self.BASE_DIR = BASE_DIR
        self.dxf_path = dxf_path
        self.doc = None
        self.x_files = [entry for entry in os.listdir(self.dxf_path) if os.path.isfile(os.path.join(self.dxf_path, entry))]
        self.files = []
        self.coordinates = dict()
        self.img_folder = os.path.join(self.BASE_DIR, "plot_figures")

    def read_file(self):
        for i in self.x_files:
            try:
                self.doc = dxf.readfile(os.path.join(self.dxf_path, i))
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

            self.coordinates[f"Needle {i+1} ({self.x_files[i]})"] = coords
    

    def plot_figures(self):

        for name, coords in self.coordinates.items():
            if not coords:
                print(f"No coordinates found for {name}, skipping...")
                continue

            coords = np.array(coords)

            rotated_coords = rotate_figure(coords)

            figure, axes = plt.subplots(figsize=(12, 9))

            axes.plot(rotated_coords[:, 0], rotated_coords[:, 1], "bo-", label="DXF data")

            axes.plot(0, 0, 'r+', markersize=10, markeredgewidth=2, label="Origin (0,0)")

            fig_width = max(rotated_coords[:, 0]) - min(rotated_coords[:, 0]) # x-axis max ja min points absolute difference
            fig_length = max(rotated_coords[:, 1]) - min(rotated_coords[:, 1]) # y-axis max ja min points absolute difference
            ellipse = Ellipse( (0, 0), fig_width, fig_length, fill = False, linestyle="--", label="Reference circle")

            axes.add_patch(ellipse)
            axes.set_aspect("equal", adjustable="box")
            axes.set_title(f"Plot for {name}")
            axes.legend()
            axes.grid(True, alpha=0.3)

            axes.set_xlabel("X (mm)")
            axes.set_ylabel("Y (mm)")

            figure.savefig(os.path.join(self.img_folder, f"{name}.png"), dpi=300)
            print(f"SAVED {name}.png")

            plt.show()
            plt.close(figure)


           
def rotate_figure(coords): # Rotates the figure to be horizontally based on the biggest legthwise difference
    pca = PCA(n_components=2)
    pca.fit(coords)

    rotated = pca.transform(coords)
    return rotated
    




    