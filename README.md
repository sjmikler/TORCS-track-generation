# Flags

1. Set up the right flags for your system and torcs installation
2. Run `python test_run.py`, which should print results of 10 (identical) races
    * if doesn't work

### Example `flags.py`:

* Linux

```
TORCS_DIR = "/home/$USER/.torcs/"
TORCS_EXEC = "/usr/games/torcs"
RACE_CONFIG = "/home/$USER/.torcs/config/raceman/quickrace.xml"
RESULTS_DIR = "/home/$USER/.torcs/results/"
```

Ignore your changes to `flags.py`, e.g. using `git update-index --assume-unchanged flags.py`.
