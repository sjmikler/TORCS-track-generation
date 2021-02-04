import logging

import numpy as np

import flags
import tools


class args:
    population_size = 10
    track_length = 4
    track_scale = 5
    log = "INFO"
    elitism = 3


logging.basicConfig(level=args.log)

with open(flags.RACE_CONFIG, "r") as f:
    race_config = f.read()

population = (
    np.random.rand(args.population_size, args.track_length, 2) * args.track_scale
)


def evaluate_population(population):
    xml_config_paths = tools.generate_configs_from_population(population)
    results = tools.run_races_read_results(xml_config_paths)

    scores = []
    for r in results:
        if (
            "timeout" not in r
            or "missing" not in r
            or r["timeout"] == True
            or r["missing"] == True
            or r["avg_best_lap_time"] == 0.0
        ):
            scores.append(0)
        else:
            scores.append(r["speed_entropy"])
    tools.clear_temp_logs()
    return scores


def crossover(p1, p2):
    cpoint = np.random.randint(1, p1.shape[0] - 1)
    return np.concatenate([p1[:cpoint], p2[cpoint:]], axis=0)


def per_mutation(p):
    swap = np.random.choice(len(p), size=2, replace=False)
    p[swap] = p[swap[::-1]]
    return p


def rnd_mutation(p):
    new_point = np.random.rand(2) * args.track_scale
    idx = np.random.choice(len(p))
    p[idx] = new_point
    return p


for generation_idx in range(100):
    fitness = evaluate_population(population)
    print(
        f"GENERATION {generation_idx:^5}, MAX_FITNESS {max(fitness):6.3f}, AVG_FITNESS {np.mean(fitness):6.3f}"
    )
    fitness = np.array(fitness) - min(fitness)
    fitness /= np.sum(fitness)

    children = []
    for _ in range(args.population_size - args.elitism):
        mama, tata = np.random.choice(
            args.population_size, size=2, p=fitness, replace=False
        )
        child = crossover(population[mama], population[tata])
        if np.random.rand() < 0.5:
            child = per_mutation(child)
        if np.random.rand() < 0.5:
            child = rnd_mutation(child)
        children.append(child)

    bests = population[np.argpartition(-fitness, kth=args.elitism)][: args.elitism]
    children.extend(bests)

    population = np.stack(children)
