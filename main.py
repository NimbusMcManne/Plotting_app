from plotting import PLOT
from compare import COMPARE
from helper import HELPER
import os

def main():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dxf_folder = os.path.join(BASE_DIR, "data")
    plot = PLOT(dxf_folder, BASE_DIR)
    compare = COMPARE(dxf_folder, BASE_DIR)
    helper = HELPER()

    plot.read_file(to_print=True)
    plot.to_array()
    
    compare.get_ellipse_shape_similarities()
    similarities = compare.get_ellipse_similarities()
    upper_ellipse_datapoints = compare.get_upper_ellipse_datapoints()
    lower_datapoints = compare.get_lower_ellipse_datapoints()

    plot.plot_similarity_dict_figures(similarities, save=False)
    plot.plot_datapoint_dict_figures(upper_ellipse_datapoints, save=False, show=True)
    #plot.plot_dict_figures(lower_datapoints, save=False)

if __name__ == "__main__":
    main()