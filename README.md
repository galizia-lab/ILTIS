# ILTIS - an _Interactive Labeled-Trial Image-stack Slicer_

![screenshot](https://github.com/grg2rsr/ILTIS/blob/master/docs/screenshot.png  "ILTIS screenshot")

## General description

This program was designed to interactively and flexibly slice datasets from functional imaging experiments along the time axis. A classical imaging experiment generates data sets of high dimensionality: The individual imaging _trials_, e.g. the response of a certain area to a stimulus is usually imaged as `(x,y)` images over time _(t)_, resulting in 3d image stacks. Additionally, different _stimuli (S)_ are given with a certain number of _repetitions (R)_, resulting in 5 dimensional data `(x,y,t,S,R)`.

This program serves the following purposes:

1.  It is a flexible data visualizer and inspector by offering interactive intensity scaling, color maps, overlays and data subselection to really see how your dataset _looks like_.
2.  It allows to select regions-of-interest (ROI) at which the data set is sliced along the temporal axis. The resulting _time traces_ are directly displayed and updated upon any change.
3. The traces can be extracted in `.csv` format, sorted to  _stimulus class S_ and _repetition R_ for subsequent data analysis.

## Usage
### Loading data
The program is still in a very early developmental stage, but already usable. Load your data from the `load` menu, trial labels can be added with the `load labels` function. Label files are expected to consist of a label in each line, with the index of each line corresponding to the respective data set. For example, if you want to load the files

+ my_trial_1.tif
+ my_trial_2.tif
+ my_trial_3.tif
+ my_trial_4.tif

and in your experiment trial 1 and 3 were `stimulus A`, 2 and 4 were `stimulus B`, then the label file has to look like

> stimulus A  
stimulus B  
stimulus A  
stimulus B  

#### File format support
Fully supported are currently any `.tif` files,  Zeiss `.lsm` files generated by 'pre-Zen' LSM 510 software (later ones might work) and `.pdb` files from TILL Vision imaging rigs. Imports for other formats can be developed, please post a request and send me an example file.

### Frame visualization
To subset the currently displayed data set use the `Data Selector` on the top right. It supports intuitive `ctrl+click`, `shift+click`, `ctrl+a` etc. to select or deselect individual trials to display. The mode of display can be set with the centrally position icons, for example switch between dF/F raw display, average over frames, or a _monochrome_ mode for individual trials with the raw data as the background optionally overlaid with the dF/F signal in a glow colormap.

### Preprocessing
Currently the datasets can be gaussian filtered along image and time axes, by convolving the x,y,t image stack with a gaussian kernel of size set in the options window. Frames that go into the background image for dF/F calculation can also be specified in the options window.

### ROI functionality
ROIs are added by simply clicking on the image, the type of ROI (circular or polygonal) can be selected in the extra `Options` window, opened by clicking on the icon in the toolbar. ROIs can be interactively resized and dragged to different regions, all traces will be updated interactively.

The `ROI Manager` supports the same multiple selection of ROIs just as the `Data Selector`. If multiple ROIs are selected, the coloring and traces display mode changes: The traces of all selected ROIs are now color coded to the ROI instead of the trial. This is useful if instead of comparing the response in two different trials, one wants to compare the response in two different areas which are within the field of view.


### Traces visualization
Depending on the selected datasets and the activated ROIs, the displayed data is sliced along the time domain under the area covered by the ROIs, each frames values are averaged. The sliced traces are color coded and can be displayed in two ways:

1) All traces with a common time base
2) sorted to stimulus identity

Both display modes can be accessed by selecting the corresponding tab of the `traces visualizer`. Both can also be detached from the main window by double-clicking on the tab, for example to move it on a separate screen. Traces are interactively updated upon any change to the ROIs or data selection.

### Traces export
After setting up all ROIs, the dataset can be sliced according to the pixels covered by the ROIs. The average value of those pixels for each frame is calculated and the resulting vectors can be written in different ways into `.csv` files:

+ `.csv - normal` writes one file per loaded dataset, with the shape (t,ROI). 
+ `.csv - sorted` writes one file per ROI and stimulus combination, with the individual columns representing the repetitions.

If a `dt` value is specified in the Options, the corresponding time vector is calculated and added to the first column of the `.csv`, with the stimulus start being set to 0, pre stimulus times are thus negative.

## Installation
Under linux, you can simply run the `run.sh`, under windows, you can double click the `run.cmd`. Both will execute the `Main.py` with `python`.

## Dependencies
All dependencies are included in standard scientific python bundles, such as the [anaconda distribution from continuum](https://www.continuum.io/downloads) 

+ python 2.7
+ matplotlib
+ scipy
+ pandas

### Coming soon
+ rigid and nonlinear transformation based movement correction
+ activity based calculation of ROIs
+ Data export and loading of internal python data objects
