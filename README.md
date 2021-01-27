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

# TORCS modifications

The directory `torcs` contains modifications needed to collect some data, as well as fixes for bugs that prevent the original code from compiling.

## Installation

1. Download the "all-in-one" source package from [the TORCS website](http://torcs.sourceforge.net/index.php?name=Sections&op=viewarticle&artid=3)
2. Copy the contents of the `torcs` directory into the extracted source code
3. Follow the installation instructions
