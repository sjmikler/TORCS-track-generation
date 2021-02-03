import numpy as np


def bin_entropy(a, bins=16, range=None):
    """Calculate entropy from bins, the same is done in the paper

    :param a: Input data
    :param bins: int or sequence, passed to np.histogram
    :param range: range of possible values, passed to np.histogram
    """

    p, _ = np.histogram(a, bins=bins, range=range, density=True)
    p1 = p[p > 0.]
    return -np.sum(p1 * np.log2(p1))


def speed_entropy(race_data):
    # ignore data from the first lap and laps after the last one
    # (they keep counting until the last player finishes)
    race_data = race_data[race_data.lap.isin([2, 3, 4])]
    # speed of all players, for all ticks
    speed = np.sqrt(race_data.vx ** 2 + race_data.vy ** 2 + race_data.vz ** 2)
    # equal size bins for now, ignore very low and very high speeds
    return bin_entropy(speed, bins=16, range=(10, 90))
