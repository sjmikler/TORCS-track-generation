import argparse

import numpy as np

import tools


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="File with the population")
    parser.add_argument("-n", "--generation", type=int, default=-1, help="Generation to load")
    parser.add_argument("-a", dest="trackgen_a", action="store_true", help="Call trackgen with '-a'")
    return parser.parse_args()


def main(args):
    population = np.load(args.file)
    generation = population[args.generation]
    n = generation.shape[0]
    tools.generate_configs_from_population(generation.reshape(n, -1, 2), trackgen_with_a=args.trackgen_a)


if __name__ == '__main__':
    args = parse_args()
    main(args)
