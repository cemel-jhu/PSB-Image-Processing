import import_ipynb
import PSM_Processing as nb

def run_study(index, band,
        scale=nb.scale,
        frequency=nb.frequency,
        direction=nb.direction,
        sigma=nb.sigma,
        height=nb.beam_height,
        width=nb.beam_width,
        flip=nb.flip,
        time_margin=nb.time_margin,
        bands=None):
  pass


def run():
  for (key, experiment) in nb.experiments.items():
    for (index, band) in experiment.bands.items():
      # We can't extract velocity data is the segment to crop is not defined.
      if band.lower == band.upper:
        continue
      data = experiment._asdict().copy()
      # change parameters in data
      run_study(index, band, **data)


if __name__ == "__main__":
  run()
