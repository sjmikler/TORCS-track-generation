import argparse
import json

from tools_evolution import Evolution


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config")
    parser.add_argument("-i", "--iterations", type=int)
    return parser.parse_args()


def main(args):
    with open(args.config) as f:
        config = json.load(f)
    evolution = Evolution(**config)
    evolution.initialize()
    evolution.print_fitness_statistics()
    for iter_ in range(args.iterations):
        evolution.step()
        evolution.print_fitness_statistics()
    evolution.save_population()


if __name__ == '__main__':
    args = parse_args()
    main(args)
