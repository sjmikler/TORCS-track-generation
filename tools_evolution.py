import numpy as np


def bin_entropy(a, bins=16):
    """Calculate entropy from bins, the same is done in the paper

    :param a: Input data
    :param bins: int or sequence, passed to np.histogram
    """

    p, _ = np.histogram(a, bins, density=True)
    p1 = p[p > 0.0]
    return -np.sum(p1 * np.log2(p1))


def speed_entropy(race_data):
    # ignore the time before the race starts (perhaps it's better to remove the first lap altogether)
    race_data = race_data[race_data.time >= 0.0]
    # speed of all players, for all ticks
    speed = np.sqrt(race_data.vx ** 2 + race_data.vy ** 2 + race_data.vz ** 2)
    # equal size bins for now
    if any(np.isnan(speed)):
        return None
    return bin_entropy(speed, bins=16)
