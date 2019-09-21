import import_ipynb
import PSM_Processing as nb


def run(band,
        scale=nb.scale,
        frequency=nb.frequency,
        direction=nb.direction,
        sigma=nb.sigma,
        beam_height=nb.beam_height,
        beam_width=nb.beam_width,
        flip=nb.flip,
        time_margin=nb.time_margin,
        bands=nb.bands):
  print(band)


def run():
  return
  for (key, experiment) in nb.experiments.items():
    for band in experiments.bands:
      # We can't extract velocity data is the segment to crop is not defined.
      if band.lower == band.upper:
        continue
      data = experiment._asdict().copy()
      # change parameters in data
      run_study(band, **data)


if __name__ == "__main__":
  run()
