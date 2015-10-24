import math
import random

# Bracket conflict struct.
class BracketConflict:
  def __init__(self, match, player1, player2, p, round, losers=False):
    self.match = match
    self.p_map = match.p_players
    self.player1 = player1
    self.player2 = player2
    self.p = p
    self.round = round
    self.losers = losers
    self.importance = self.CalculateImportance()

  def CalculateImportance(self):
    return self.p / ((self.round + 1)**2)

  def __hash__(self):
    return hash((tuple(sorted([self.player1.name, self.player2.name])), self.round, self.losers))

  def __eq__(self, other):
    return self.match == other.match and (self.player1 == other.player1 and self.player2 == other.player2 or \
           self.player1 == other.player2 and self.player2 == other.player1)

  def __str__(self):
    str_out = ""
    if self.losers:
      str_out += "Losers"
    else:
      str_out += "Winners"
    str_out += " round " + str(self.round) + "\n" + self.player1.name + ", " + self.player2.name + \
               "\np = " + str(self.p) + "\nimportance = " + str(self.importance) + "\n" + \
               self.match.PrettifyProbMap(self.p_map[0]) + "\n" + self.match.PrettifyProbMap(self.p_map[1])
    return str_out

  def __repr__(self):
    return self.__str__()

# Pool conflict struct.
class PoolConflict:
  def __init__(self, player1, player2):
    self.player1 = player1
    self.player2 = player2
    self.importance = self.CalculateImportance()

  def CalculateImportance(self):
    return 1

  def __hash__(self):
    return hash(tuple(sorted([self.player1.name, self.player2.name])))

  def __eq__(self, other):
    return self.player1 == other.player1 and self.player2 == other.player2 or \
           self.player1 == other.player2 and self.player2 == other.player1

  def __str__(self):
    str_out = ""
    if self.losers:
      str_out += "Losers"
    else:
      str_out += "Winners"
    str_out += self.player1.name + ", " + self.player2.name + "\nimportance = " + str(self.importance)
    return str_out

  def __repr__(self):
    return self.__str__()

# Set of bracket conflicts.
class ConflictSet:
  def __init__(self):
    self.num_conflicts = 0
    self.conflicts = {}
    self.e_importance = 0.0

  def AddConflict(self, conflict):
    if not conflict in self.conflicts:
      self.conflicts[conflict] = True
      self.num_conflicts += 1
      self.e_importance += conflict.importance

  def GetConflictsByImportance(self):
    return sorted(self.conflicts.keys(), key=lambda conflict: conflict.importance, reverse=True)

  def GetConflictsString(self):
    str_conflicts = ""
    e_conflicts, e_importance, e_conflicts_filtered, e_importance_filtered = 0.0, 0.0, 0.0, 0.0
    filtered_count = 0

    sorted_conflicts = self.GetConflictsByImportance()
    for conflict in sorted_conflicts:
      if conflict.p >= .1:
        filtered_count += 1
        e_conflicts_filtered += conflict.p
        e_importance_filtered += conflict.importance
      str_conflicts += str(conflict) + "\n\n"
      e_conflicts += conflict.p
      e_importance += conflict.importance
    return "Num conflicts: " + str(self.num_conflicts) + \
           "\nNum conflicts (filtered): " + str(filtered_count) + \
           "\nExpected conflicts: " + str(e_conflicts) + \
           "\nExpected conflicts (filtered): " + str(e_conflicts_filtered) + \
           "\nConflict importance: " + str(e_importance) + \
           "\nConflict importance (filtered): " + str(e_importance_filtered) + "\n" + str_conflicts

class AnnealingState:
  def __init__(self, score, seeds, loadable_seeds):
    self.score = score
    self.seeds = seeds
    self.loadable_seeds = loadable_seeds
    self.conflict_set = None

  def SelectConflict(self):
    rnd = random.uniform(0.0, self.score)
    total = 0.0
    for conflict in self.conflict_set.conflicts.keys():
      total += conflict.importance
      if rnd <= total:
        return conflict
    return None

  def GetNearbyState(self, player_map, range):
    # Choose players to swap
    conflict = self.SelectConflict()
    player = conflict.player1
    if conflict.player1.p_win(conflict.player2) > random.random():
      player = conflict.player2
    opponent = player
    while opponent == player:
      opponent = player_map.GetRandomPlayerWithinSkill(player.skill, range)

    # Swap the players in the seed lists
    seeds = list(self.seeds)
    i1, i2, = seeds.index(player), seeds.index(opponent)
    seeds[i1], seeds[i2] = seeds[i2], seeds[i1]
    loadable_seeds = list(self.loadable_seeds)
    i1, i2, = loadable_seeds.index(player), loadable_seeds.index(opponent)
    loadable_seeds[i1], loadable_seeds[i2] = loadable_seeds[i2], loadable_seeds[i1]
    return AnnealingState(0.0, seeds, loadable_seeds)

class AnnealingManager:
  def __init__(self, config, player_map):
    self.config = config
    self.player_map = player_map
    self.conflicts = None

  def RunSimulatedAnnealing(self, config, initial_state, gen_conflicts, params):
    s = AnnealingState(-1, initial_state[0], initial_state[1])
    e_conflicts, s.score, s.conflict_set = gen_conflicts(params, None)
    s_cur = s
    print "Best score: " + str(s.score)

    # Run simulated annealing
    k = self.config["annealing_rounds"]
    for i in xrange(0, k):
      #if k % 100 == 0:
      #  print ".",
      T = Temperature(i, k)

      # Generate the new state.
      s_new = s_cur.GetNearbyState(self.player_map, self.config["tolerance"])
      e_conflicts, s_new.score, s_new.conflict_set = gen_conflicts(params, s_new.loadable_seeds)

      # Possibly advance to the new state
      if P(s_cur.score, s_new.score, T) >= random.random():
        s_cur = s_new
        #print "Cur score :", s_cur.score, e_conflicts
        if s_cur.score < s.score:
          s = s_cur
          print "Best score:", s.score, e_conflicts
          if s.score < self.config["annealing_goal"]:
            break

    print "Done simulated annealing"
    self.conflicts = s.conflict_set

# Simulated annealing functions
def Temperature(i, k):
  return 1 - i/k

def P(e, e2, T):
  if e2 < e:
    return 1
  return math.exp((e - e2) / T)
