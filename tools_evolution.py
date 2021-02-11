import numpy as np

import tools
from tools_bezier import get_track, get_track_stats

class Evolution:
    """Single objective evolution"""

    def __init__(self, n_population: int, n_children: int, n_elite: int, track_length: int, track_scale: float,
                 p_mutation: float, eta_mutation: float, objective="speed_entropy"):
        self.n_population = n_population
        self.n_children = n_children
        self.n_elite = n_elite
        self.track_length = track_length
        self.track_scale = track_scale
        self.p_mutation = p_mutation
        self.eta_mutation = eta_mutation
        self.objective = objective
        self.population = np.array([])
        self.fitness = np.array([])
        self.generation = 0

    def initialize(self):
        self.population = np.random.rand(self.n_population, self.track_length * 2) * self.track_scale
        self.fitness = evaluate_population(self.population, self.objective)
        self.generation = 0

    def step(self):
        self.generation += 1

        parents = roulette_selection(self.fitness, self.n_children)
        children = []
        for i, j in zip(parents[:self.n_children // 2], parents[self.n_children // 2:]):
            c1, c2 = single_point_crossover(self.population[i], self.population[j])
            c1 = polynomial_mutation(c1, 0, self.track_scale, self.p_mutation, self.eta_mutation)
            c2 = polynomial_mutation(c2, 0, self.track_scale, self.p_mutation, self.eta_mutation)
            children.append(c1)
            children.append(c2)

        children = np.vstack(children)
        children_fitness = evaluate_population(children, self.objective)

        # selection with elitism
        best_parents = np.argsort(-self.fitness)[:self.n_elite]
        best_children = np.argsort(-children_fitness)[:self.n_population - self.n_elite]
        self.population = np.vstack([self.population[best_parents], children[best_children]])
        self.fitness = np.hstack([self.fitness[best_parents], children_fitness[best_children]])

    def print_fitness_statistics(self):
        print(
            f"GENERATION {self.generation:^5}, MAX_FITNESS {max(self.fitness):6.3f}, AVG_FITNESS {np.mean(self.fitness):6.3f}"
        )

    def print_specimen_fitness(self):
        for i, score in enumerate(self.fitness):
            print(f"specimen{i}: {score:6.3f}")

    def save_population(self, prefix=None):
        n = self.population.shape[0]
        tools.generate_configs_from_population(self.population.reshape(n, -1, 2))


def bin_entropy(a, bins=16, range=None, weights=None):
    """Calculate entropy from bins, the same is done in the paper
    :param a: Input data
    :param bins: int or sequence, passed to np.histogram
    :param range: range of possible values, passed to np.histogram
    :param range: weights of input values, passed to np.histogram
    """

    p, _ = np.histogram(a, bins=bins, range=range, weights=weights)
    p1 = p[p > 0]
    if len(p1) > 0:
        p1 = p1 / p1.sum()
        return -np.sum(p1 * np.log2(p1))
    else:
        return 0.


def speed_entropy(race_data, n_laps=4):
    # ignore data from the first lap and laps after the last one
    # (they keep counting until the last player finishes)
    race_data = race_data[race_data.lap.between(2, n_laps, inclusive=True)]
    # speed of all players, for all ticks
    speed = np.sqrt(race_data.vx ** 2 + race_data.vy ** 2 + race_data.vz ** 2)
    # equal size bins for now, ignore very low and very high speeds
    return bin_entropy(speed, bins=16, range=(10, 90))

def curves_entropy(points):
    segments, curves = get_track(points)
    turns, lengths = get_track_stats(segments, curves)
    length = sum(lengths)
    turns = np.array(turns)
    lengths = np.array(lengths) / length
    bins = [-np.inf, -7, -5, -4, -3, -2, -1.5, -1, -0.5, -0.25, -0.1, -0.05, -0.02, -0.01, -0.005,
            0.005, 0.01, 0.02, 0.05, 0.1, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 7, np.inf]

    return bin_entropy(turns, bins, range=None, weights=lengths)

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
    if isinstance(x_min, np.ndarray):
        x_min = x_min[mask]
    if isinstance(x_max, np.ndarray):
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


def roulette_selection(scores, n_children):
    scores = scores - scores.min()
    s = scores.sum()
    if s == 0:
        p = np.full_like(scores, 1 / scores.shape[0])
    else:
        p = scores / s
    indices = np.random.choice(scores.shape[0], n_children, replace=True, p=p)
    return indices


def evaluate_population(population, objective="speed_entropy"):
    n = population.shape[0]
    xml_config_paths = tools.generate_configs_from_population(population.reshape(n, -1, 2))
    results = tools.run_races_read_results(xml_config_paths)

    scores = []
    for r in results:
        if (
                "timeout" not in r
                or "missing" not in r
                or r["timeout"] == True
                or r["missing"] == True
                or r["invalid"] == True
                or r["avg_best_lap_time"] == 0.0
        ):
            scores.append(0)
        else:
            scores.append(r[objective])
    tools.clear_temp_logs()
    return np.array(scores)
