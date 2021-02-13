import logging
import os
import re
import shutil
import signal
import subprocess
from os import path

import pandas as pd
import pandas.errors

import flags
import tools_bezier
import tools_evolution


def avg(x):
    x = list(x)
    return sum(x) / len(x) if len(x) else 0


def clear_temp_logs():
    """Our logs might take A LOT of disk space, it is important to clear them."""

    logging.info("Clearing logs...")
    for fname in os.listdir(flags.RESULTS_DIR):
        if fname.startswith("temp_config"):
            fullpath = path.join(flags.RESULTS_DIR, fname)
            shutil.rmtree(fullpath)


def find_final_results(race_basename):
    """Return latest xml `results` log"""

    exact_dir = path.join(flags.RESULTS_DIR, race_basename)
    logs = os.listdir(exact_dir)
    logs = [l for l in logs if l.startswith("results")]
    if not logs:
        logging.info(f"No FINAL logs found for {race_basename}...")
        return None
    latest_log = max(logs)  # maximal should be the latest
    with open(path.join(exact_dir, latest_log), "r") as f:
        result = f.read()
    return result


def read_final_results(xml_result_content):
    """Read basic things from xml results log"""

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


def find_read_final_results(race_basename):
    xml_result_content = find_final_results(race_basename)
    return read_final_results(xml_result_content) if xml_result_content else None


def find_race_data(race_basename):
    """Find the data generated during the race"""
    exact_dir = path.join(flags.RESULTS_DIR, race_basename)
    logs = os.listdir(exact_dir)
    logs = [l for l in logs if l.startswith("data")]
    if not logs:
        logging.info(f"No RACE logs found for {race_basename}...")
        return None
    latest_log = max(logs)  # maximal should be the latest
    try:
        data = pd.read_csv(path.join(exact_dir, latest_log), index_col=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        logging.info(f"Empty or corrupted DataFrame found for {race_basename}...")
        return None
    return data


def read_race_data(race_data):
    """Read entropy data from race results log"""
    results = {}
    if not validate_race_data(race_data, 3):
        return {"invalid": True}
    speed_entropy = tools_evolution.speed_entropy(race_data, 3)
    if speed_entropy is None:
        return None
    results["speed_entropy"] = speed_entropy
    results["invalid"] = False
    return results


def find_read_race_data(race_basename):
    """Find and read the data generated during the race"""
    race_data = find_race_data(race_basename)
    if race_data is None:
        return None
    results = read_race_data(race_data)
    if results is None:
        logging.info(f"Speed data for {race_basename} contained NaN...")
        return None
    return results


def validate_race_data(race_data, expected_laps):
    """Make sure that at least one bot was able to finish the race"""
    if race_data is None:
        return False
    # the race seems to keep going for some time after the final lap even for the last player
    if race_data.lap.max() < expected_laps + 1:
        return False
    return True


def generate_configs_from_population(population):
    with open(flags.RACE_CONFIG, "r") as f:
        race_config = f.read()

    processes = []
    xml_config_paths = []
    for idx, specimen in enumerate(population):
        track_name = f"specimen{idx:03}"
        segments, curves = tools_bezier.get_track(specimen)
        xml, pit_stop = tools_bezier.to_xml(segments, curves)
        xml = tools_bezier.get_full_xml_track_file(track_name, xml, pit_stop)

        new_track_path = path.join(flags.TRACKS_DIR, track_name)
        if not path.exists(new_track_path):
            os.makedirs(new_track_path)

        with open(path.join(new_track_path, f"{track_name}.xml"), "w") as f:
            f.write(xml)

        for config_path in xml_config_paths:
            with open(config_path, "r") as f:
                f.read()

        process = subprocess.Popen(
            args=["trackgen", "-c", "evolution", "-n", track_name],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        processes.append(process)

        new_race_config = re.sub(
            '<attstr name="name" val="NAME_PLACEHOLDER"/>',
            f'<attstr name="name" val="{track_name}"/>',
            race_config,
        )

        new_race_config_path = path.join(os.getcwd(), "temp", f"temp_config{idx}.xml")
        with open(new_race_config_path, "w") as f:
            f.write(new_race_config)
        xml_config_paths.append(new_race_config_path)

    for idx, process in enumerate(processes):
        logging.debug(f"CREATING CONFIG FOR RACE {idx:^5}...")
        process.wait(timeout=4)
        err = process.stderr.read()
        if err:
            logging.info(f"trackgen STDERR: {err}")
    return xml_config_paths


def run_races_read_results(xml_config_paths):
    """Run many races at once (multiprocessing) and output results."""

    processes = []
    try:
        for config_path in xml_config_paths:
            with open(config_path, "r") as f:
                f.read()

            process = subprocess.Popen(
                args=[flags.TORCS_EXEC, "-r", config_path],
                cwd=flags.TORCS_DIR,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                preexec_fn=os.setsid,
            )
            processes.append(process)

        timed_out = []
        for idx, process in enumerate(processes):
            try:
                logging.debug(f"WAITING FOR RACE {idx:^5}...")
                process.wait(timeout=5)
                err = process.stderr.read()
                if err:
                    logging.info(f"torcs STDERR: {err}")
            except subprocess.TimeoutExpired:
                logging.info(f"RACE {idx:^5} TIMEOUT!")
                timed_out.append(idx)
                pgid = os.getpgid(process.pid)
                os.killpg(pgid, signal.SIGTERM)
    except:
        for process in processes:
            if process.poll() is None:
                pgid = os.getpgid(process.pid)
                os.killpg(pgid, signal.SIGTERM)
        raise

    all_results = []
    for idx, config_path in enumerate(xml_config_paths):
        logging.debug(f"READING RESULTS OF RACE {idx:^5}...")
        if idx in timed_out:
            all_results.append({"timeout": True})
            continue

        basename = path.basename(config_path)
        if basename.endswith(".xml"):
            basename = basename[:-4]

        final_results = find_read_final_results(basename)
        race_results = find_read_race_data(basename)

        if final_results is None or race_results is None:
            logging.info(f"RACE {idx:^5} MISSING!")
            all_results.append({"missing": True})
            continue

        results = {**final_results, **race_results}
        results["timeout"] = False
        results["missing"] = False
        all_results.append(results)
    return all_results
