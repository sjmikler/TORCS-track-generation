import numpy as np
import tools
import tools_bezier
import subprocess
import flags
from os import path
import os
import re

POPULATION_SIZE = 10
TRACK_LENGTH = 4
TRACK_SCALE = 10

with open(flags.RACE_CONFIG, "r") as f:
    race_config = f.read()

for _ in range(10):
    population = np.random.rand(POPULATION_SIZE, TRACK_LENGTH, 2) * TRACK_SCALE

    processes = []
    xml_config_paths = []
    for idx, specimen in enumerate(population):
        segments, curves = tools_bezier.get_track(specimen)
        xml = tools_bezier.to_xml(segments, curves)
        xml = tools_bezier.get_full_xml_track_file(xml)

        new_track_path = path.join(flags.TRACKS_DIR, f"specimen{idx}")
        if not path.exists(new_track_path):
            os.makedirs(new_track_path)

        with open(path.join(new_track_path, f"specimen{idx}.xml"), "w") as f:
            f.write(xml)

        for config_path in xml_config_paths:
            with open(config_path, "r") as f:
                f.read()
        process = subprocess.Popen(
            args=["trackgen", "-c", "evolution", "-n", f"specimen{idx}"],
            # cwd=flags.TORCS_DIR,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        processes.append(process)

        new_race_config = re.sub(
            '<attstr name="name" val="NAME_PLACEHOLDER"/>',
            f'<attstr name="name" val="specimen{idx}"/>',
            race_config,
        )

        new_race_config_path = path.join(os.getcwd(), "temp", f"temp_config{idx}.xml")
        with open(new_race_config_path, "w") as f:
            f.write(new_race_config)
        xml_config_paths.append(new_race_config_path)

    for process in processes:
        process.wait()
        print(process.stderr.read())

    results = tools.run_races_read_results(xml_config_paths)
    for r in results:
        print(r)
