import os
import re
from os import path


def add_ghost_racer(race_config, run_idx):
    drivers_section = '<section name="Drivers">'
    drivers_loc = race_config.find(drivers_section) + len(drivers_section)
    ghost_driver_section = f"""
      <section name="5">
        <attstr name="module" val="ghost_driver{run_idx}"/>
      </section>
      """
    race_config = race_config[:drivers_loc] + \
                  ghost_driver_section + \
                  race_config[drivers_loc:]
    return race_config


def find_results(results_dir, run_idx):
    exact_dir = path.join(results_dir, f'temp_config{run_idx}')
    logs = list(os.listdir(exact_dir))
    latest_log = max(logs)
    with open(path.join(exact_dir, latest_log), 'r') as f:
        result = f.read()
    return result


def read_results(xml_content):
    results = {}
    lap_time = re.findall(r'<attnum name="best lap time" val="(\d+\.\d+)"/>',
                          xml_content)
    lap_time = sum(float(t) for t in lap_time) / len(lap_time)
    results['avg_best_lap_time'] = lap_time

    max_dmg = re.findall(r'<attnum name="dammages" val="(\d+)"/>',
                         xml_content)
    max_dmg = max(float(t) for t in max_dmg)
    results['max_damage'] = max_dmg
    return results


def find_and_read_results(results_dir, run_idx):
    xml_content = find_results(results_dir, run_idx)
    return read_results(xml_content)
