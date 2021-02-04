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


def speed_entropy(race_data, n_laps=4):
    # ignore data from the first lap and laps after the last one
    # (they keep counting until the last player finishes)
    race_data = race_data[race_data.lap.between(2, n_laps, inclusive=True)]
    # speed of all players, for all ticks
    speed = np.sqrt(race_data.vx ** 2 + race_data.vy ** 2 + race_data.vz ** 2)
    # equal size bins for now, ignore very low and very high speeds
    return bin_entropy(speed, bins=16, range=(10, 90))


def single_point_crossover(x1, x2):
    y1 = x1.copy()
    y2 = x2.copy()
    n = np.random.choice(x1.shape[0])
    y1[n:] = x2[n:]
    y2[n:] = x1[n:]
    return y1, y2


def polynomial_mutation(x, x_min, x_max, p, eta):
    """From https://www.iitk.ac.in/kangal/papers/k2012016.pdf"""
    y = x.copy()
    mask = np.random.random(x.shape) < p
    x = x[mask]
    x_min = x_min[mask]
    x_max = x_max[mask]

    u = np.random.random(x.shape)
    delta = np.where(
        u < 0.5,
        np.power(2 * u, 1 / (1 + eta)) - 1,
        1 - np.power(2 - 2 * u, 1 / (1 + eta)),
    )
    y[mask] = np.where(
        u < 0.5,
        x + delta * (x - x_min),
        x + delta * (x_max - x)
    )
    return y


def roulette_selection(x, scores, n_children):
    p = scores - scores.min()
    ps = p.sum()
    if ps == 0:
        p = np.full_like(scores, 1 / scores.shape[0])
    else:
        p /= ps
    indices = np.random.choice(x.shape[0], n_children, replace=True, p=p)
    return x[indices]
