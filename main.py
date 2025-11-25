from plotting import PLOT
from compare import COMPARE
from helper import HELPER
from shapes import SHAPE
import os

d_type = "dynamic"
s_type = "static"

def main():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dxf_folder = os.path.join(BASE_DIR, "data")
    plot = PLOT(dxf_folder, BASE_DIR)
    compare = COMPARE(dxf_folder, BASE_DIR)
    helper = HELPER()
    shapes = SHAPE()

    plot.read_file(to_print=True)
    plot.to_array()
    plot.compute_dimensions()

    plot.take_average_width_height()

    compare.get_ellipse_areas(plot)
    compare.get_diamond_areas(plot)
    compare.get_rectangle_areas(plot)
    compare.get_figure_areas(plot)


    # # First ellipse
    # compare.get_ellipse_shape_similarities(plot, typ=d_type)
    # ellipse_similarities_dynamic = compare.get_ellipse_similarities().copy()

    # plot.plot_similarity_dict_figures(ellipse_similarities_dynamic, typ=d_type, save=True)

    # # Second ellipse
    # compare.get_ellipse_shape_similarities(plot, typ=s_type)
    # ellipse_similarities_static = compare.get_ellipse_similarities().copy()

    # plot.plot_similarity_dict_figures(ellipse_similarities_static, typ=s_type, save=True)
    


    # # First diamond
    # compare.get_diamond_shape_similarities(plot, typ=d_type)
    # diamond_similarities_dynamic = compare.get_diamond_similarities().copy()

    # plot.plot_similarity_dict_figures(diamond_similarities_dynamic, typ=d_type, shape="diamond", save=True)

    # # Second diamond
    # compare.get_diamond_shape_similarities(plot, typ=s_type)
    # diamond_similarities_static = compare.get_diamond_similarities().copy()

    # plot.plot_similarity_dict_figures(diamond_similarities_static, typ=s_type, shape="diamond", save=True)


    # First rectangle
    compare.get_rectangle_shape_similarities(plot, typ=d_type)
    rectangle_similarities_dynamic = compare.get_rectangle_similarities().copy()

    plot.plot_similarity_dict_figures(rectangle_similarities_dynamic, typ=d_type, shape="rectangle", save=True)

    # Second rectangle
    compare.get_rectangle_shape_similarities(plot, typ=s_type)
    rectangle_similarities_static = compare.get_rectangle_similarities().copy()

    plot.plot_similarity_dict_figures(rectangle_similarities_static, typ=s_type, shape="rectangle", save=True)


    # See if halves work correctly
    # pos_ellipse_pts = compare.get_upper_h_ellipse_datapoints().copy()
    # pos_fig_pts = compare.get_upper_h_figure_datapoints().copy()

    # plot.plot_datapoint_dict_figures(pos_ellipse_pts, shape="ellipse", save=True, show=False)
    # plot.plot_datapoint_dict_figures(pos_fig_pts, shape="figure", save=True, show=False)

if __name__ == "__main__":
    main()