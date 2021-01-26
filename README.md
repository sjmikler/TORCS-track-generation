# Flags

1. Set up the right flags for your system and torcs installation
2. Run `python test_run.py`, which should print results of 10 (identical) races
    * if doesn't work

### Example `flags.py`:

* Windows

```
TORCS_DIR = "D:\\Games\\torcs"
TORCS_EXEC = "D:\\Games\\torcs\\wtorcs.exe"
RACE_CONFIG = "D:\\Games\\torcs\\config\\raceman\\quickrace.xml"
RESULTS_DIR = "C:\\Users\\gaha\\AppData\\Local\\torcs\\results"
```

* Linux

```
TORCS_DIR = "/home/konrad/.torcs/"
TORCS_EXEC = "/usr/games/torcs"
RACE_CONFIG = "/home/konrad/.torcs/config/raceman/quickrace.xml"
RESULTS_DIR = "/home/konrad/.torcs/results/"
```
