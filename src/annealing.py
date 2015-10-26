import math
import random

import bracket
import round_robin
import util

class AnnealingManager:
  def __init__(self, config, player_map):
    self.config = config
    self.player_map = player_map
    self.conflicts = None

  def RunSimulatedAnnealing(self):
    round = Round(self.config, self.config["num_pools"], self.config["pool_type"], self.player_map)
    round.Simulate()
    s = AnnealingState(round.conflicts.score, round.players, round.conflicts)
    s_cur = s
    print "Best score: " + str(s.score)

    # Run simulated annealing
    k = self.config["annealing_rounds"]
    for i in xrange(0, k):
      T = self.Temperature(i, k)

      # Generate the new state.
      s_new = s_cur.GetNewState(self.player_map, self.config["tolerance"])
      round.SetSeeds(s_new.seeds)
      round.Simulate()
      s_new.score = round.conflicts.score
      s_new.conflicts = round.conflicts

      # Possibly advance to the new state
      if self.P(s_cur.score, s_new.score, T) >= random.random():
        s_cur = s_new
        #print "Cur score :", s_cur.score, e_conflicts
        if s_cur.score < s.score:
          s = s_cur
          print "Best score:", s.score, s.conflicts.e_conflicts
          if s.score < self.config["annealing_goal"]:
            break

    print "Done simulated annealing"
    self.conflicts = s.conflicts

  def Temperature(self, i, k):
    return 1 - (float(i)/k)

  def P(self, e, e2, T):
    if e2 < e:
      return 1
    return math.exp((e - e2) / T)

class Round:
  def __init__(self, config, num_pools, pool_type, player_map):
    self.config = config
    self.num_pools = num_pools
    self.players = player_map.GetPlayersBySkill()
    self.num_players = len(self.players)
    self.players_per_pool = self.num_players / self.num_pools

    pool_players = [[] for i in xrange(self.num_pools)]
    print pool_players, self.num_pools
    for i in xrange(0, self.num_players):
      j = i % self.num_pools
      if j > (self.num_pools / 2) - 1:
        j = self.num_pools - 1 - j
      pool_players[j].append(self.players[i])

    self.pools = []
    for i in xrange(0, self.num_pools):
      if pool_type == util.PoolType.BRACKET:
        self.pools.append(bracket.BracketPool(self.config, pool_players[i]))
      elif pool_type == util.PoolType.ROUND_ROBIN:
        self.pools.append(round_robin.RoundRobinPool(self.config, pool_players[i]))

    self.players = []
    for pool in self.pools:
      self.players.extend(pool.GetSeeds())
      
    self.need_simulation = True

  def SetSeeds(self, seeds):
    for i in xrange(0, self.num_pools):
      start = self.players_per_pool * i
      self.pools[i].SetSeeds(seeds[start: start + self.players_per_pool])
    self.need_simulation = True

  def GetSeeds(self):
    return list(self.players)

  def Simulate(self):
    if not self.need_simulation:
      return
    self.conflicts = ConflictSet()
    for pool in self.pools:
      pool.Simulate(self.conflicts)
    self.need_simulation = False

class AnnealingState:
  def __init__(self, score, seeds, conflicts):
    self.score = score
    self.seeds = seeds
    self.sorted_seeds = []
    self.conflicts = conflicts

  def SelectConflict(self):
    rnd = random.uniform(0.0, self.score)
    total = 0.0
    for conflict in self.conflicts.conflicts.keys():
      total += conflict.score
      if rnd <= total:
        return conflict
    return None

  def GetNewState(self, player_map, range):
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
    return AnnealingState(0.0, seeds, None)

# Set of bracket conflicts.
class ConflictSet:
  def __init__(self):
    self.num_conflicts = 0
    self.conflicts = {}
    self.score = 0.0
    self.e_conflicts = 0.0

  def AddConflict(self, conflict):
    if not conflict in self.conflicts:
      self.conflicts[conflict] = True
      self.num_conflicts += 1
      self.score += conflict.score
      self.e_conflicts += conflict.p

  def GetConflictsByImportance(self):
    return sorted(self.conflicts.keys(), key=lambda conflict: conflict.score, reverse=True)

  def GetConflictsString(self):
    str_conflicts = ""
    e_conflicts_filtered, e_importance_filtered = 0.0, 0.0
    filtered_count = 0

    sorted_conflicts = self.GetConflictsByImportance()
    for conflict in sorted_conflicts:
      if conflict.p >= .1:
        filtered_count += 1
        e_conflicts_filtered += conflict.p
        e_importance_filtered += conflict.score
      str_conflicts += str(conflict) + "\n\n"
    return "Num conflicts: " + str(self.num_conflicts) + \
           "\nNum conflicts (filtered): " + str(filtered_count) + \
           "\nConflict score: " + str(self.score) + \
           "\nConflict score (filtered): " + str(e_importance_filtered) + \
           "\nExpected conflicts: " + str(self.e_conflicts) + \
           "\nExpected conflicts (filtered): " + str(e_conflicts_filtered) + "\n" + str_conflicts
