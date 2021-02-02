import os
import re
import subprocess
from os import path

import pandas as pd

import flags
import tools_bezier


def avg(x):
    x = list(x)
    return sum(x) / len(x) if len(x) else 0


def find_file(results_dir, race_basename, file_kind):
    """Return latest xml log in folder `race_basename`"""

    exact_dir = path.join(results_dir, race_basename)
    logs = os.listdir(exact_dir)
    logs = [l for l in logs if l.startswith(file_kind)]
    latest_log = max(logs)  # maximal should be the latest
    with open(path.join(exact_dir, latest_log), "r") as f:
        result = f.read()
    return result


def read_results(xml_result_content):
    """Read basic things from xml log.
    To be improved, depending of our needs..."""

    results = {}
    lap_time = re.findall(
        r'<attnum name="best lap time" val="(\d+\.\d+)"/>', xml_result_content
    )
    lap_time = avg(float(t) for t in lap_time)
    results["avg_best_lap_time"] = lap_time

    all_dmg = re.findall(r'<attnum name="dammages" val="(\d+)"/>', xml_result_content)
    max_dmg = max(float(t) for t in all_dmg)
    results["max_damage"] = max_dmg
    avg_dmg = avg(float(t) for t in all_dmg)
    results["avg_damage"] = avg_dmg

    top_speed = re.findall(
        r'<attnum name="top speed" val="(\d+\.\d+)"/>', xml_result_content
    )
    top_speed = avg(float(t) for t in top_speed)
    results["avg_top_speed"] = top_speed
    return results


def find_read_results(results_dir, race_basename):
    xml_result_content = find_file(results_dir, race_basename, "results")
    return read_results(xml_result_content)


def read_data(data_str):
    """Read data from the CSV file generated during the race."""
    return pd.read_csv(data_str, index_col=False)


def find_read_data(results_dir, race_basename):
    data_str = find_file(results_dir, race_basename, "data")
    return read_data(data_str)


def run_races_read_results(xml_config_paths):
    """Run many races at once (multiprocessing) and output results."""

    processes = []
    for config_path in xml_config_paths:
        with open(config_path, "r") as f:
            f.read()

        process = subprocess.Popen(
            args=[flags.TORCS_EXEC, "-r", config_path],
            cwd=flags.TORCS_DIR,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        processes.append(process)

    timed_out = []
    for idx, process in enumerate(processes):
        try:
            process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            print("RACE TIMEOUT!")
            timed_out.append(idx)
            process.terminate()

    all_results = []
    for idx, config_path in enumerate(xml_config_paths):
        if idx in timed_out:
            all_results.append({"timeout": True})
            continue

        basename = path.basename(config_path)
        if basename.endswith(".xml"):
            basename = basename[:-4]

        results = find_read_results(flags.RESULTS_DIR, basename)
        results["timeout"] = False
        all_results.append(results)
    return all_results


def generate_configs_from_population(population):
    with open(flags.RACE_CONFIG, "r") as f:
        race_config = f.read()

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
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
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
        process.wait(timeout=4)
        print("trackgen STDERR:", process.stderr.read())
    return xml_config_paths
