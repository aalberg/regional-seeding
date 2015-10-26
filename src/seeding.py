import sys
import random

import annealing
import player_data
import util

config = {
  "config_file": "../cfg/config.txt",
  "player_in_file": "../data/ss18/players_in_ss18_1.txt",
  "player_out_file": "../data/ss18/players_out_ss18_1.txt",
  "bracket_out_file": "../data/ss18/bracket_out_ss18_1.txt",
  #"player_in_file": "../data/test/players_in.txt",
  #"player_out_file": "../data/test/players_out.txt",
  #"bracket_out_file": "../data/test/bracket_out.txt",
  "tolerance": 0,
  "num_pools": 1,
  "pool_type": util.PoolType.BRACKET,
  "num_spaces_per_round": 10,
  "use_advanced_bracket_seeding": True,
  "annealing_rounds": 1000,
  "annealing_goal": -1.0,
  # Currently unused
  "swap_byes": False,
  "bye_swap_tolerance": 0,
  "seed_fraction": 1,
  # Debug params
  "probabilistic_bracket_out_file": "../data/ss18/bracket_out_ss18_1_2.txt",
  "conflicts_out_file": "../data/ss18/conflicts_out_ss18_1.txt",
  "start_seed": 123,
}
config_types = {
  "config_file": "string",
  "player_in_file": "string",
  "player_out_file": "string",
  "bracket_out_file": "string",
  "tolerance": "int",
  "swap_byes": "bool",
  "bye_swap_tolerance": "int",
  "seed_fraction": "int",
  "num_spaces_per_round": "int",
  "use_advanced_bracket_seeding": "bool",
  "annealing_rounds": "int",
  "annealing_goal": "float",
}

# Main.
def main():
  util.LoadConfig(config, config_types)
  player_map = player_data.PlayerMap()
  util.LoadPlayers(config, player_map)
  print ""

  random.seed(config["start_seed"])
  player_map.PadWithByes()
  #bracket_inst.BuildBracket(player_map)
  #players_str = bracket_inst.GetPlayersBySeedString()
  #util.WriteStr((players_str, config["player_out_file"]))
  #bracket_str = bracket_inst.GetBracketString()
  #util.WriteStr((bracket_str, config["bracket_out_file"]))
  print "-"*60

  manager = annealing.AnnealingManager(config, player_map)
  manager.RunSimulatedAnnealing()

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

    #if command[1] == "bracket":
    #  param = (bracket_inst.GetBracketString(), config["bracket_out_file"])
    #elif command[1] == "winners":
    #  param = (bracket_inst.GetWinnersBracketString(), config["bracket_out_file"])
    #elif command[1] == "losers":
    #  param = (bracket_inst.GetLosersBracketString(), config["bracket_out_file"])
    #elif command[1] == "prob":
    #  param = (bracket_inst.GetProbabilisticBracketString(), config["probabilistic_bracket_out_file"])
    if command[1] == "seeds":
      param = (round.GetPlayersBySeedString(), config["player_out_file"])
    elif command[1] == "players":
      param = (player_map.GetPlayersBySkillString(), None)
    elif command[1] == "conflicts":
      param = (manager.conflicts.GetConflictsString(), config["conflicts_out_file"])
    else:
      print "Command not found"
      continue

    func(param)

if __name__ == "__main__":
  main()
