# PSM Image Processing :movie_camera:

This repository provides some of the source code used for [insert paper here](#).
Source images and results may be available upon contact.

---

This research was sponsored by the U.S. Air Force Office of Scientific Research
(AFOSR) under grant \# FA9550-18-1-0071. This material is based upon work
supported by the National Science Foundation Graduate Research Fellowship under
Grant No. 2017245441. The authors recognize Dr. Craig Johnson at Drexel
University for his help with transmission electron microscopy. The authors also
appreciate insightful discussions with Professor H¨ael Mughrabi of
Erlangen-N¨urnberg University in Germany and Professor Jaroslav Pol´ak of the
Institute of Physics of Materials at Academy of Sciences of the Czech Republic

---

Provided a video of micro pillars being loaded, this code determines the rate
of PSM propagation, and the embryonic size of PSMs.

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
