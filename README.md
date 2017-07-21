# regional-seeding
Regional tournament bracket seeding program for use with Challonge or smash.gg

Current version: 1.1.2

### Requirements
Python 2.7

Python 3 not supported

### Note
This program is not going to be perfect. The goal is to aid TO's by doing most of the initial work up front, not replace hand seeding.

### Quick Start
Edit `cfg/config.txt`.
Add the lines:
```
player_in_file path/to/player/file
seeds_out_file_header path/seeds/should/go/to
```

Edit path/to/player/file.
Add lines in the format:
```
player1,score1,region1
player2,score2,region2
... etc
```

From the command line:

1. Run `main.py`
2. When the command prompt shows, type `write seeds`

The seeded pool(s) will be located in `seeds_out_file_header[number].txt` (where [number] is the pool number).

### Input
Input is read from the file pointed to by `player_in_file`. The input is in a csv format:
```
player1,score1,region1
player2,score2,region2
... etc
```
csv format can be easily generated with Excel or a comparable program.

### Possible Player Skill Bins
```
10 is whoever the best expected winners are, usually no more than 4
9 is the great players right below them
8 is really good players, 8-12 or so on the PR
7 is for the rest of the PR
6 is for borderline PR
5 is for people known to be solid
4 is for generally competent up and comers
3 is for less good players that can at least L cancel
2 or lower is completely new player
```

More skill levels and fractional levels can be added as needed. However, the spacing between skill levels is defined such that a player level L has a 75% chance of beating a player of level L-1, and a 100% chance of beating a player of level L-2. Skill levels must be positive.

### Command Line Output
Several types of output are available from the built in command line. There are two main output commands: `print` and `write`. `print` will cause the desired output to be printed to the console. `write` will write the desired output to a file specified in the configuration options. Using `print` is not recommended, as the output may be large and some consoles (Windows command prompt) do not allow copying of output text.

The possible outputs are listed below
```
pools     Print information relevant to the pool. Bracket pools print a stylized bracket. Round robin pools print a list of players in the pool.
debug     Print detailed information relevant to the pool simulation. Bracket pools print a stylized bracket showing the probabilities of players reaching each slot in the bracket. Round robin pools print a list of players in the pool.
conflicts Print the regional conflicts, including an estimated severity of the conflict and the pair of players involved. A summary of conflict information is printed at the top of the list.
seeds     Print the final seed list. These lists are importable into challonge using the 'The Order of the Participants List' style seeding.
players   Lists the players in the order they were read, before any seeding has taken place. Has no effect with write
```

### Configuration
Edit `config.txt` in cfg to change the configuration of the program. To set the value of a configuration option, enter a line in `config.txt` with the name of the option followed by the new value, separated by a single space

The full set of configuration options is listed below. All paths are relative to main.py.
```
player_in_file          The location of the player input file.
out_folder              The folder to store output files in.
pools_out_file_header   The header of the pool output files.
debug_out_file_header   The header of the pool debug info output files.
conflicts_out_file      The location of the conflict output file.
seeds_out_file_header   The header of the seeds output files.
tolerance               Skill tolerance when swapping players. The range is inclusive.
num_pools               Number of pools.
pool_type               1 for bracket pools, 2 for round robin.
num_spaces_per_round    Spaces per bracket round for indenting bracket matches in output files.
annealing_rounds        Number of simulated annealing rounds to output.
annealing_goal          Goal of annealing. If the cumulative conflict score drops below this, annealing will stop.
use_fixed_seed          Use a fixed seed for random number generation. Results in the same bracket being generated for the same input file and config settings.
```

Default settings:
```
player_in_file          data/ss18/players_in_ss18_1.txt
out_folder              data/ss18/output/
pools_out_file_header   pool_
debug_out_file_header   debug_
conflicts_out_file      conflicts.txt
seeds_out_file_header   seeds_
tolerance               0
num_pools               1
pool_type               1
num_spaces_per_round    10
annealing_rounds        1000
annealing_goal          -1.0
use_fixed_seed          1
```
