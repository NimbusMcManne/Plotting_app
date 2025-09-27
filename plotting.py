import matplotlib.pyplot as plt
import numpy as np
import ezdxf as dxf
import os
import sys

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

    def to_array(self):
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
            self.coordinates[f"needle{i+1}"] = coords
    

    def plot_figures(self):

        for name, coords in self.coordinates.items():
            coords = np.array(coords)

            figure, axes = plt.subplots()

            axes.plot(coords[:, 0], coords[:, 1], "bo-", label="DXF data")

            circle = plt.Circle( (0, 0), max(coords[:, 0]) , fill = False, linestyle="--", label="Reference circle")
            axes.add_patch(circle)

            axes.set_aspect("equal", adjustable="box")
            axes.set_title(f"Plot for {name}")
            axes.legend()
            axes.grid(True, alpha=0.3)

            figure.savefig(os.path.join(self.img_folder, f"{name}.png"), dpi=300)
            print(f"SAVED {name}.png")

            plt.show()
            plt.close(figure)
           
        
    




    