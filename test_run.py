import tools
import flags
from os import path
import time
import os
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--num_races", type=int, default=1)
parser.add_argument("--track_length", type=int, default=4)
parser.add_argument("--track_scale", type=int, default=10)
args = parser.parse_args()

with open(flags.RACE_CONFIG, "r") as f:
    race_config = f.read()

population = np.random.rand(args.num_races, args.track_length, 2) * args.track_scale

t = time.time()
xml_config_paths = tools.generate_configs_from_population(population)
results = tools.run_races_read_results(xml_config_paths)
tt = time.time() - t

for i, r in enumerate(results):
    print(f"{i}: {r}")
print(f"Time taken: {tt:.2f}s ({tt/args.num_races:.2f}s per race)")
