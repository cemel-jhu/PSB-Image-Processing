import import_ipynb
import PSM_Processing as nb
import geometry
import numpy as np
import argparse
import sys


def run_study(study_name,
              parameter,
              experiment,
              scale=nb.scale,
              frequency=nb.frequency,
              direction=nb.direction,
              sigma=nb.sigma,
              beam_height=nb.beam_height,
              beam_width=nb.beam_width,
              flip=nb.flip,
              time_margin=nb.time_margin,
              bands=None):

    if not bands:
        print("run_study must be called with bands", file=sys.stderr)

    load_ext = ""

    # Do bulk preporcessing
    # Load images
    # Note that these are all important:
    # borders=borders,
    # frequency
    # resize=resize,
    # margin_x=margin_x,
    # if in paramters, recompute = True
    if parameter in set(["frequency", "beam_height", "beam_width"]):
        load_ext = "_" + study_name
    images = nb.load_images(path="images{}".format(load_ext),
                            experiment=experiment,
                            bmps="images/{}/*.bmp",
                            recompute=False,
                            frequency=frequency,
                            beam_width=beam_width,
                            beam_height=beam_height)

    beam_height, beam_width = images[list(images.keys())[0]].shape
    times = list(images.keys())

    # Realigm images
    # direction, flip
    # if direction, recompute = true
    if parameter in set(["direction", "flip"]):
        load_ext = "_" + study_name
    lengths, lins = nb.extract_length((beam_height, beam_width),
                                      direction=direction)
    cube = nb.shear_images(images,
                           recompute=False,
                           path="extracted{}".format(load_ext),
                           experiment=experiment,
                           lins=lins,
                           flip=flip)
    cube = np.array(list(cube.values()))
    # We do some basic filtering on the cube
    cube = nb.clean(cube)

    # Extract events
    if parameter in set(["sigma", "time_margin"]):
        load_ext = "_" + study_name
    vs = nb.extract_events(cube,
                           recompute=False,
                           path="vs{}".format(load_ext),
                           experiment=experiment,
                           times=times,
                           sigma=sigma,
                           lengths=lengths,
                           time_margin=time_margin)

    # Run individual band parts
    csv = np.zeros([len(bands), 13])
    row = 0
    for (index, band) in bands.items():
        # We can't extract velocity data in a segment where crop is not defined.
        if band.lower == band.upper:
            continue
        # change parameters in data
        scaled, unscaled = nb.split_vs(vs, start=band.start, width=band.width)
        lin, indices, points, points_raw = nb.extract_points(
            scaled,
            unscaled,
            beam_width=beam_width,
            width=band.width,
            time_margin=time_margin,
            times=times)
        # Average said events for a representation of event occurence
        # within an entire PSB.
        XY = np.mean(scaled, axis=0)
        raw = np.mean(unscaled, axis=0)
        hull, hull_raw = nb.extract_hull(images,
                                         points,
                                         points_raw,
                                         indices,
                                         beam_width=beam_width,
                                         time_margin=time_margin)
        # Probably allow for name as well.
        nb.export_profiles(images,
                           scaled,
                           unscaled,
                           beam_width=beam_width,
                           plotted=False,
                           times=times,
                           width=band.width,
                           experiment=experiment,
                           band=index,
                           time_margin=time_margin,
                           study_name=load_ext)

        # Extract clean hull data
        filtered = cleaned_hull(lin, hull)
        np.savetxt(
            "csv/hull_{}_band_{}_{}.csv".format(experiment, band, study_name),
            np.array(filtered).T,
            delimiter=",",
        )

        # Should probably do a if upper > lower. But we'll have to look at the
        # profiles to figure out the crops.
        try:
            print()
            format(index, experiment)
            # Extract clean profile data
            convex_hull = geomtery.convex_hull(filtered)
            supports, rectangularity = score_profile(convex_hull)
            # Extract velocity data.
            line = nb.fit_segment(np.array([lin, hull]),
                                  plot=False,
                                  lower=band.lower,
                                  upper=band.upper,
                                  right=False)
            # Extract embryo data
            embryo = nb.embryo(np.array([lin, hull]), lower=2.5, upper=16)
            csv[row, :] = [
                index, experiment, supports, rectangularity, line.slope,
                line.intercept, line.rvalue
            ] + list(embyro)
            row += 1
        except Exception as e:
            print(("Could not extract data for "
                   "band {} in experiment {}: {}.").format(
                       index, experiment, e.message),
                  file=sys.stderr)
    np.savetxt(
        "csv/result_{}_{}.csv".format(experiment, study_name),
        np.array(csv).T,
        delimiter=",",
        header=("band, experiment, hull.supports, hull.rect, line.slope, "
                "line.intercept, line.rvalue, line.pvalue, embryo.start, "
                "embryo.end, embryo.length, embryo.std, embryo.rvalue"))


def run(study_name, parameter, parameters):
    for (key, experiment) in nb.experiments.items():
        data = experiment._asdict().copy()
        if parameter not in data:
            raise argparse.ArgumentError(
                "Parameter name must be found in nb.Record")
        for value in parameters:
            data[parameter] = value
            run_study("{}_{}_{}".format(study_name, parameter, value),
                      parameter, key, **data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs a parametric study.')
    parser.add_argument('parameters',
                        metavar='N',
                        type=float,
                        nargs='+',
                        help='The parameters to experimentally iterate over.')
    parser.add_argument('--study',
                        default="study",
                        help='The name to call this study.')
    parser.add_argument('--parameter',
                        required=True,
                        help='The parameter to run the study over.')
    args = parser.parse_args()
    run(args.study, args.parameter, args.parameters)
