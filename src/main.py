from src.plotting import PLOT
from src.compare import COMPARE
from src.helper import HELPER
from src.shapes import SHAPE
import os
import argparse


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_folder", type=str, default="/data", help="Path to the DXF folder")
    parser.add_argument("--save_path", type=str, default="/plot_figures", help="Path to save the plots")
    parser.add_argument("--shape", type=str, default="ellipse", help="Type of shape (ellipse, diamond, rectangle, figure)")
    parser.add_argument("--type", type=str, default="dynamic", help="Type of comparison (dynamic or static)")
    parser.add_argument("--save", type=bool, default=True, help="Save the plots (True or False)")
    parser.add_argument("--show", type=bool, default=False, help="Show the plots (True or False)")
    args = parser.parse_args()     

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    plot = PLOT(args.data_folder, BASE_DIR)
    compare = COMPARE(args.data_folder, BASE_DIR)
    helper = HELPER()
    shapes = SHAPE()

    plot.read_file(to_print=True)
    plot.to_array()
    plot.compute_dimensions()
    plot.take_average_width_height()
    compare.get_figure_areas(plot)

    args.shape = args.shape.lower()
    args.type = args.type.lower()

    print(args.show)
    if args.shape == "ellipse":
        compare.get_ellipse_areas(plot)
        compare.get_ellipse_shape_similarities(plot, typ=args.type)
        ellipse_similarities_dynamic = compare.get_ellipse_similarities().copy()
        plot.plot_similarity_dict_figures(ellipse_similarities_dynamic, save_path=args.save_path, typ=args.type, shape="ellipse", save=args.save, show=args.show)
    elif args.shape == "diamond":
        compare.get_diamond_areas(plot)
        compare.get_diamond_shape_similarities(plot, typ=args.type)
        diamond_similarities_dynamic = compare.get_diamond_similarities().copy()
        plot.plot_similarity_dict_figures(diamond_similarities_dynamic, save_path=args.save_path, typ=args.type, shape="diamond", save=args.save, show=args.show)
    elif args.shape == "rectangle":
        compare.get_rectangle_areas(plot)
        compare.get_rectangle_shape_similarities(plot, typ=args.type)
        rectangle_similarities_dynamic = compare.get_rectangle_similarities().copy()
        plot.plot_similarity_dict_figures(rectangle_similarities_dynamic, save_path=args.save_path, typ=args.type, shape="rectangle", save=args.save, show=args.show)


if __name__ == "__main__":
    main()