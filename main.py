from plotting import PLOT
from compare import COMPARE
import os

def main():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dxf_folder = os.path.join(BASE_DIR, "data")
    plot = PLOT(dxf_folder, BASE_DIR)
    compare = COMPARE(dxf_folder, BASE_DIR)

    plot.read_file(to_print=True)
    plot.to_array()
    
    
    compare.get_shape_similarities()
    similarities = compare.get_ellipse_similarities()

    plot.plot_figures(similarities)

if __name__ == "__main__":
    main()