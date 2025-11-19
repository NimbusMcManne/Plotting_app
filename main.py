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
    ellipse_similarities = compare.get_ellipse_similarities()
    # upper_ellipse_datapoints = compare.get_upper_ellipse_datapoints()
    # lower_datapoints = compare.get_lower_ellipse_datapoints()

    compare.get_diamond_shape_similarities()
    diamond_similarities = compare.get_diamond_similarities()
    diamond_dat = compare.get_upper_diamond_datapoints()
    fig_dat = compare.get_upper_figure_datapoints()

    plot.plot_similarity_dict_figures(ellipse_similarities, save=True)
    plot.plot_similarity_dict_figures(diamond_similarities, shape="diamond", save=True)

    plot.plot_datapoint_dict_figures(diamond_dat, shape="diamond", save=False, show=False)
    plot.plot_datapoint_dict_figures(fig_dat, shape="figure", save=False, show=False)
    #plot.plot_dict_figures(lower_datapoints, save=False)

if __name__ == "__main__":
    main()