import sys
import random

import annealing
import player_data
import util

config = {
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
  "annealing_rounds": 1000,
  "annealing_goal": -1.0,
  # Currently unused
  "swap_byes": False,
  "bye_swap_tolerance": 0,
  "seed_fraction": 1,
  # Debug params
  "start_seed": 123,
}
config_types = {
  "config_file": "string",
  "player_in_file": "string",
  "pools_out_file_header": "string",
  "debug_out_file_header": "string",
  "conflicts_out_file": "string",
  "seeds_out_file_header": "string",
  "tolerance": "int",
  "num_pools": "int",
  "pool_type": "int",
  "num_spaces_per_round": "int",
  "annealing_rounds": "int",
  "annealing_goal": "float",
  # Currently unused
  "swap_byes": "bool",
  "bye_swap_tolerance": "int",
  "seed_fraction": "int",
  # Debug params
  "start_seed": "int",
}

# Main.
def main():
  util.LoadConfig(config, config_types)
  player_map = player_data.PlayerMap()
  util.LoadPlayers(config, player_map)
  print ""

  random.seed(config["start_seed"])
  player_map.PadWithByes()

  manager = annealing.AnnealingManager(config, player_map)
  print "-"*60
  manager.RunSimulatedAnnealing()
  print "-"*60

  command = ""
  while not command == "quit":
    command = raw_input(" $ ").split()
    if command[0] == "print":
      func = util.PrintStr
    elif command[0] == "write":
      func = util.WriteStr
    elif command == "quit":
      print "Exiting"
      break
    else:
      print "Command not found"
      continue

    if command[1] == "pools":
      manager.round.WritePools(func, config["pools_out_file_header"])
    elif command[1] == "debug":
      manager.round.WritePools(func, config["debug_out_file_header"], True)
    elif command[1] == "conflicts":
      manager.round.WriteConflicts(func, config["conflicts_out_file"])
    elif command[1] == "seeds":
      manager.round.WritePoolSeeds(func, config["seeds_out_file_header"])
    elif command[1] == "players":
      func((player_map.GetPlayersBySkillString(), None))
    else:
      print "Command not found"
      continue

if __name__ == "__main__":
  main()
