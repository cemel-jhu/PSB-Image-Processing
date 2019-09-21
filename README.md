# PSM Image Processing :movie_camera:

This repository provides some of the source code used for [insert paper here](#).
Source images and results may be available upon contact, note that they are too
large to host on github.

---

This research was sponsored by the U.S. Air Force Office of Scientific Research
(AFOSR) under grant \# FA9550-18-1-0071. This material is based upon work
supported by the National Science Foundation Graduate Research Fellowship under
Grant DGE-1746891. The authors recognize Dr. Craig Johnson at Drexel
University for his help with transmission electron microscopy. The authors also
appreciate insightful discussions with Professor H¨ael Mughrabi of
Erlangen-N¨urnberg University in Germany and Professor Jaroslav Pol´ak of the
Institute of Physics of Materials at Academy of Sciences of the Czech Republic

---

Provided a video of micro pillars being loaded, this code determines the rate
of PSM propagation, and the embryonic size of PSMs.

## Installation

Install this package via pip i.e `pip install git+git://github.com/cemel-jhu/PSM-Image-Processing@master`.
Alternatively, clone this repository and use `pip install .`

To install updates run `pip install git+git://github.com/cemel-jhu/PSM-Image-Processing@master --upgrade`.

## Usage

Interactively run the notebook with `jupyter notebook .`, or import needed functions from the module:
```python
import PSMProcessing as psm
...
```

To run bulk studies, implement the `parameter_study.py` script provided. Its usage is as follows:

```text
usage: parameter_study.py [-h] [--study STUDY] --parameter PARAMETER N [N ...]
parameter_study.py: The following arguments are required: N, --parameter
```

For example: `python parameter_study.py --study=sigma_variation
--parameter=sigma 0.35 0.65 1` runs a parameter study on the filtering
hyperparameter `sigma`. For other parameters see below.

## Analysis Variables
The study of a given PSM band is performed based on these global variables.
Align these parameters with your work.
```python
# Run specific variables
experiment = 32  # The experiment number. Images for this experiment should be in folder {experiment}/
band = 3  # The band to examine within the experiment
export_gifs = True  # Whether gifs should be exported
interactive = True  # Whether interactive parts of the script should be run.
recompute = False  # Forces recomputation. Warning, will potentially overwrite
                   # other variables.

# Experiment specific variables. These will be overwritten
# if the experiment has already been analyzed.
scale = 768 / 40.27  # Pixels to um ratio.
frequency = 75  # The frequency of loading in Hz
direction = 2. / 3  # The slope of the PSBs in the experiment relative to the image.
                    # Seemingly allows for margin of error.
beam_height = 600  # In pixels
beam_width = 180  # in pixels
flip = True  # All PSM slopes should be positive. If the slope is negative, a
             # reflection is performed on the picture.

# Band specific variables
start = 0  # The start offset of a given band.
width = beam_height  # The width of the given band.

# New experiment specific variables. These values will be ignored
# unless no records exist for the given variable.
# Image loading specific variables.
resize = 0  # Scale factor by which the image should be resized. Set 0 for no resizing.
borders = [50, 140, 30, 40]  # Left, Right, Top, Bottom.
                             # Cropping margins for the processed images.
margin_x = [20, 3]  # The margin to provide a partially cropped beam,
                    # when determining how to crop the height

# Event capture specific variables.
time_margin = 15  # How much of the video to ignore at the beginning and end
sigma = 0.65  # Smoothing deviation for filtering procedures
```

## Velocity Determination
The general procedure for velocity determination is as follows:
```python
# Each frame is warped along the PSB direction. In practice this was
# implemented iteratively with `scipy.interpolate.interp2d`.
warped_frames = []
for frame in frames:
  warped_frames += warp(frame)

# Each frame is cropped to a particular PSB at the discretion of the researcher.
canidate_psb = []
for frame in warped_frames:
  canidate_psb += crop(frame)

# The time cube of dimension [time, width, height]
# is flipped to [height, width, time].
canidate_profile_source = flip(canidate_psb)

# Iterate over and extract the profiles for each time slice of size
# [width, height].
profiles = []
for slice in canidate_profile_source:
  profiles += detect_profile(slice)

# Use one of the aggregation methods to extract a representative profile.
velocity_profile = aggregate_profiles(profile)
```

## Embryonic Width detection
The general procedure for embryonic width determination is as follows:
```python
potential_embryo = []
for cycle, displacement in sorted(profile):
  potential_embryo += [(cycle, displacement)]
  qq_fits += [qq_fit(potential_embryo.displacements)]

embyro = potential_embryo[:argmin(qq_fits)]
embyro_start = min(embryo.displacements)
embyro_end = max(embryo.displacements)
embryo_length = embryo_end - embyro_start
```
