# Flags

1. Set up the right flags for your system and torcs installation
2. Run `python test_run.py --num_races=10`, which should print results of 10 (identical) races

### Example `flags.py`:
```
TORCS_DIR = "/home/$USER/.torcs/"
TORCS_EXEC = "/usr/games/torcs"
RACE_CONFIG = "/home/$USER/.torcs/config/raceman/quickrace.xml"
RESULTS_DIR = "/home/$USER/.torcs/results/"
```

Ignore your changes to `flags.py`, e.g. using `git update-index --assume-unchanged flags.py`.
