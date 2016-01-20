import math
import random
import threading
import time

import bracket
import round_robin
import util

class AnnealingManager:
  def __init__(self, config, player_map):
    self.config = config
    self.player_map = player_map
    self.saved_states = {}
    self.round = None

  def RunSimulatedAnnealing(self):
    self.round = Round(self.config, self.config["num_pools"], self.config["pool_type"], self.player_map)
    self.round.Simulate()
    s = AnnealingState(self.round.conflicts.score, self.round.players, self.round.conflicts)
    s_cur = s
    print "Best score: " + str(s.score)

    times = []
    start = time.clock()

    # Run simulated annealing
    k = self.config["annealing_rounds"]
    for i in xrange(0, k):
      T = self.Temperature(i, k)

      # Generate the new state.
      s_new = s_cur.GetNewState(self.player_map, self.config["tolerance"])
      self.round.SetSeeds(s_new.seeds)
      self.round.Simulate()
      s_new.score = self.round.conflicts.score
      s_new.conflicts = self.round.conflicts

      times.append(self.round.sim_time)

      # Possibly advance to the new state
      if self.P(s_cur.score, s_new.score, T) >= random.random():
        s_cur = s_new
        #print "Cur score :", s_cur.score, e_conflicts
        if s_cur.score < s.score:
          s = s_cur
          print "Best score:", s.score, s.conflicts.e_conflicts
          if s.score < self.config["annealing_goal"]:
            break

    self.round.SetSeeds(s.seeds)
    self.round.Simulate()
    times.append(self.round.sim_time)
    self.round.VerifyPlayers()
    print "Done simulated annealing"
    end = time.clock()

    print "Total annealing time:", end - start
    print "Mean simulation time:", sum(times) / float(len(times))

  def ForceSimulate(self):
    if not self.round == None:
      self.round.need_simulation = True
      self.round.Simulate()
      print "New score", self.round.conflicts.score, self.round.conflicts.e_conflicts

  def SaveState(self, name):
    if not self.round == None:
      self.saved_states[name] = self.round.GetSeeds()
      print "Saved state:", name
    else:
      print "Could not save state:", name

  def LoadState(self, name):
    if not self.round == None and name in self.saved_states:
      self.round.SetSeeds(self.saved_states[name])
      print "Loaded state:", name
    else:
      print "Could not load state:", name

  def SwapPlayers(self, player1, player2):
    if player1 == player2 or self.round == None:
      return

    i1 = -1
    i2 = -1
    players = self.round.GetSeeds()
    print players
    for i in xrange(len(players)):
      if players[i].name == player1:
        i1 = i
      elif players[i].name == player2:
        i2 = i
      if i1 >= 0 and i2 >= 0:
        players[i1], players[i2] = players[i2], players[i1]
        self.round.SetSeeds(players)
        print "Swapped", player1, "with", player2, i1, i2
        return
    if i1 < 0:
      print "Could not find player", player1
    if i2 < 0:
      print "Could not find player", player2

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
    for i in xrange(0, self.num_players):
      j = i % (2*self.num_pools)
      if j > self.num_pools - 1:
        j = 2*self.num_pools - 1 - j
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

    self.VerifyPlayers()

  # Debug verification in case something is really messed up and there are duplicate players. (Cava is not The Brig no matter how much he wishes he was).
  def VerifyPlayers(self):
    error = False
    for i in xrange(0, len(self.players)-1):
      for j in xrange(i+1, len(self.players)):
        if self.players[i] == self.players[j]:
          print "ERROR", self.players[i], self.players[j]
          print self.players
          error = True
    if error:
      None.hi

  def SetSeeds(self, seeds):
    self.players = seeds
    for i in xrange(0, self.num_pools):
      start = self.players_per_pool * i
      self.pools[i].SetSeeds(seeds[start: start + self.players_per_pool])
    self.need_simulation = True

  def GetSeeds(self):
    return list(self.players)

  def Simulate(self):
    if not self.need_simulation:
      return
    start = time.clock()
    self.conflicts = ConflictSet()
    
    for pool in self.pools:
      pool.Simulate(self.conflicts)

    self.need_simulation = False
    end = time.clock()
    self.sim_time = end - start

  def WritePools(self, function, file_prefix="", debug = False):
    for i in xrange(0, self.num_pools):
      path = file_prefix + str(i + 1) + ".txt"
      if not debug:
        function((self.pools[i].GetPoolString(), path))
      else:
        function((self.pools[i].GetDebugString(), path))

  def WriteConflicts(self, function, file):
    function((self.conflicts.GetConflictsString(), file))

  def WritePoolSeeds(self, function, file_prefix=""):
    self.VerifyPlayers()
    for i in xrange(0, self.num_pools):
      pool_str = '\n'.join([player.name for player in self.pools[i].GetSortedSeeds()])
      function((pool_str, file_prefix + str(i + 1) + ".txt"))

class AnnealingState:
  def __init__(self, score, seeds, conflicts):
    self.score = score
    self.seeds = seeds
    self.sorted_seeds = []
    self.conflicts = conflicts

  def SelectConflict(self):
    temp_score = self.score
    for conflict in self.conflicts.conflicts.keys():
      temp_score -= conflict.score
    rnd = random.uniform(0.0, temp_score)
    total = 0.0
    for conflict in self.conflicts.conflicts.keys():
      if conflict.player1.is_bye or conflict.player2.is_bye:
        continue
      total += conflict.score
      if rnd <= total:
        return conflict
    return None

  def GetNewState(self, player_map, range):
    # Choose players to swap
    conflict = self.SelectConflict()
    if conflict == None:
      return self
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

  # TODO(aalberg) Speed this up
  def AppendConflictSet(self, conflict_set):
    self.conflicts.update(conflict_set.conflicts)
    self.num_conflicts += conflict_set.num_conflicts
    self.score += conflict_set.score
    self.e_conflicts += conflict_set.e_conflicts
    #for conflict in conflict_set.conflicts:
    #  self.AddConflict(conflict)

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

if __name__ == "__main__":
  print "Run main.py"
