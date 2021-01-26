import tools
import flags
import subprocess
from os import path
import os

NUM_RACES = 10

if __name__ == "__main__":
    with open(flags.RACE_CONFIG, 'r') as f:
        race_config = f.read()

    processes = []
    for run_idx in range(NUM_RACES):
        new_race_config_path = path.join(os.getcwd(),
                                         'temp',
                                         f'temp_config{run_idx}.xml')
        with open(new_race_config_path, 'w') as f:
            f.write(race_config)

        process = subprocess.Popen(
            args=[flags.TORCS_EXEC, '-r', new_race_config_path],
            cwd=flags.TORCS_DIR,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        processes.append(process)

    for process in processes:
        process.wait()

    for run_idx in range(NUM_RACES):
        result = tools.find_and_read_results(flags.RESULTS_DIR, run_idx)
        print(f'run {run_idx} result:', result)
