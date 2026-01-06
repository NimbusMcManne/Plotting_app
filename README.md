# Simple plotting app 
This is a simple plotting app made to plot needle cross-sections from DXF files and compare them to a reference shape.

## Installation

Create a virtual environment preferably with python version 3.14.2.

```bash
python -m venv .venv
```

Activate the virtual environment.
```bash
.venv\Scripts\activate
```

Install the requirements.
```bash
pip install -r requirements.txt
```

## Usage
In the project folder run the code with:
```bash
python -m src/main --data_folder /data --save_path /plot_figures --shape ellipse --type dynamic --save True --show False
```

```
--data_folder
```
This should be the absolute path to the folder containing the DXF files of needles cross-sections (or other objects).

```
--save_path
```
This should be the absolute path to the folder where the plots will be saved.

```
--shape
```
This should be the shape to compare the cross-sections to. It can be "ellipse", "diamond" or "rectangle".

```
--type
```
This sets the shape type to be "dynamic" or "static". "Dynamic" means that the shape is computed for each cross-section, while "static" means that the shape is computed for the average needle cross-section.

```
--save
--show
```
These set the save and show parameters for the plots. Default is "save=True" and "show=False".