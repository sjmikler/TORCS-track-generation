import os
import re
from os import path
import subprocess
import flags


def avg(x):
    x = list(x)
    return sum(x) / len(x)


def find_results(results_dir, race_basename):
    """Return latest xml log in folder `race_basename`"""

    exact_dir = path.join(results_dir, race_basename)
    logs = list(os.listdir(exact_dir))
    latest_log = max(logs)  # max should be latest
    with open(path.join(exact_dir, latest_log), 'r') as f:
        result = f.read()
    return result


def read_results(xml_result_content):
    """Read basic things from xml log.
    To be improved, depending of our needs..."""

    results = {}
    lap_time = re.findall(r'<attnum name="best lap time" val="(\d+\.\d+)"/>',
                          xml_result_content)
    lap_time = avg(float(t) for t in lap_time)
    results['avg_best_lap_time'] = lap_time

    max_dmg = re.findall(r'<attnum name="dammages" val="(\d+)"/>',
                         xml_result_content)
    max_dmg = max(float(t) for t in max_dmg)
    results['max_damage'] = max_dmg

    top_speed = re.findall(r'<attnum name="top speed" val="(\d+\.\d+)"/>',
                           xml_result_content)
    top_speed = avg(float(t) for t in top_speed)
    results['avg_top_speed'] = top_speed
    return results


def find_read_results(results_dir, race_basename):
    xml_result_content = find_results(results_dir, race_basename)
    return read_results(xml_result_content)


def run_races_read_results(xml_config_paths):
    processes = []
    for config_path in xml_config_paths:
        with open(config_path, 'r') as f:
            f.read()

        process = subprocess.Popen(
            args=[flags.TORCS_EXEC, '-r', config_path],
            cwd=flags.TORCS_DIR,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        processes.append(process)

    for process in processes:
        process.wait()

    all_results = []
    for config_path in xml_config_paths:
        basename = path.basename(config_path)
        if basename.endswith('.xml'):
            basename = basename[:-4]

        results = find_read_results(flags.RESULTS_DIR, basename)
        all_results.append(results)
    return all_results
