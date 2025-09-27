from plotting import PLOT
import matplotlib.pyplot as plt
import os

def main():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    dxf_folder = os.path.join(BASE_DIR, "data")
    plot = PLOT(dxf_folder, BASE_DIR)

    plot.read_file()
    plot.to_array()
    plot.plot_figures()


if __name__ == "__main__":
    main()