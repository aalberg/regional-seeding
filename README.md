# regional-seeding
Regional tournament bracket seeding program

### Requirements
Python 2.7
Python 3 not supported

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
cd into src
Run `seeding.py`
When the command prompt shows, type `write seeds`

The seeded pool(s) will be located in `path/seeds/should/go/to<number>.txt` (where <number> is the pool number).

### Input
Input is read from the file pointed to by `player_in_file`. The input is in a csv format:
```
player1,score1,region1
player2,score2,region2
... etc
```
csv format can be easily generated with Excel or a comparable program.

### Command Line Output
Several types of output are available from the built in command line. There are two main output commands: `print` and `write`. `print` will cause the desired output to be printed to the console. `write` will write the desired output to a file specified in the configuration options. Using `print` is not recommended, as the output may be large and some consoles (Windows command prompt) do not allow copying of output text.

The possible outputs are listed below
```
pools     Print information relevant to the pool. Bracket pools print a stylized bracket. Round robin pools print a list of players in the pool.
debug     Print detailed information relevant to the pool simulation. Bracket pools print a stylized bracket showing the probabilities of players reaching each slot in the bracket. Round robin pools print a list of players in the pool.
conflicts Print the regional conflicts, including an estimated severity of the conflict and the pair of players involved. A summary of conflict information is printed at the top of the list.
seeds     Print the final seed list. These lists are importable into challonge using the 'The Order of the Participants List' style seeding.
players   Lists the players in the order they were read, before any seeding has taken place.
```

### Configuration
Edit `config.txt` in cfg to change the configuration of the program. To set the value of a configuration option, enter a line in `config.txt` with the name of the option followed by the new value, separated by a single space

"config_file": "../cfg/config.txt",
"player_in_file": "../data/ss18/players_in_ss18_1.txt",
"pools_out_file_header": "../data/ss18/output/pool_",
"debug_out_file_header": "../data/ss18/output/debug_",
"conflicts_out_file": "../data/ss18/output/conflicts.txt",
"seeds_out_file_header": "../data/ss18/output/seeds_",
"tolerance": 0,
"num_pools": 1,
"pool_type": util.PoolType.BRACKET,
"num_spaces_per_round": 10,
"use_advanced_bracket_seeding": True,
"annealing_rounds": 1000,
"annealing_goal": -1.0,