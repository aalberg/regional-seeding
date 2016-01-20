import os
import sys
import random

import annealing
import player_data
import util

config = {
  "config_file": "cfg/config.txt",
  "player_in_file": "data/ss18/players_in_ss18_1.txt",
  "out_folder": "data/ss18/output/",
  "pools_out_file_header": "pool_",
  "debug_out_file_header": "debug_",
  "conflicts_out_file": "conflicts.txt",
  "seeds_out_file_header": "seeds_",
  "tolerance": 0,
  "num_pools": 1,
  "pool_type": util.PoolType.BRACKET,
  "num_spaces_per_round": 10,
  "annealing_rounds": 1000,
  "annealing_goal": -1.0,
  "use_fixed_seed": 1,
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
  "out_folder": "string",
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
  "use_fixed_seed": "int",
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

  if config["use_fixed_seed"] == 1:
    random.seed(config["start_seed"])
  player_map.PadWithByes()

  manager = annealing.AnnealingManager(config, player_map)
  print "-"*60
  manager.RunSimulatedAnnealing()
  print "-"*60

  command = ""
  while not command == "quit":
    # Process input.
    command = raw_input(" $ ").split()
    for i in xrange(len(command)):
      command[i] = command[i].strip()
    command = filter(None, command)

    num_parts = len(command)
    # Command length 1 (quit or version)
    if len(command) == 1:
      if command[0] == "quit":
        print "Exiting"
        break
      elif command[0] == "version":
        print "1.0.1"
        break
      elif command[0] == "simulate":
        manager.ForceSimulate()
      else:
        print "Command not found"
        continue
    # Command length 2 (save, load, swap, print, write)
    elif len(command) == 2:
      if command[0] == "save":
        manager.SaveState(command[1])
        continue
      elif command[0] == "load":
        manager.LoadState(command[1])
        continue
      elif command[0] == "swap":
        players = ' '.join(command[1:]).split(',')
        if len(players) == 2:
          manager.SwapPlayers(players[0], players[1])
        else:
          print "Command not found"
        continue
      elif command[0] == "print":
        func = util.PrintStr
      elif command[0] == "write":
        func = util.WriteStr
      else:
        print "Command not found"
        continue

      if command[1] == "pools":
        manager.round.WritePools(func, config["out_folder"] + config["pools_out_file_header"])
      elif command[1] == "debug":
        manager.round.WritePools(func, config["out_folder"] + config["debug_out_file_header"], True)
      elif command[1] == "conflicts":
        manager.round.WriteConflicts(func, config["out_folder"] + config["conflicts_out_file"])
      elif command[1] == "seeds":
        manager.round.WritePoolSeeds(func, config["out_folder"] + config["seeds_out_file_header"])
      elif command[1] == "players":
        func((player_map.GetPlayersBySkillString(), None))
      else:
        print "Command not found"
        continue
    else:
      print "Command not found"
      continue

if __name__ == "__main__":
  print "Run main.py"
