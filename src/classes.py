import random
import annealing

# Player struct.
class Player:
  def __init__(self, new_name="bye", new_skill=-1, new_region="n/a", new_is_bye=False):
    self.name = new_name
    self.skill = new_skill
    self.region = new_region
    self.is_bye = new_is_bye

  # TODO: Improve the probability model of players winning a match
  def p_win(self, opponent):
    diff = self.skill - opponent.skill
    if diff >= 2:
      return 1
    elif diff <= -2:
      return 0
    return .5 + .25*diff

  def __str__(self):
    return self.name

  def __repr__(self):
    return self.name + ", " + str(self.skill) + ", " + self.region

  def __hash__(self):
    return hash(self.name)

# Single bracket match.
class BracketMatch:
  def __init__(self, new_players=[None, None], new_seeds=(-1, -1), new_winner_to=None, new_loser_to=None,
               new_round=-1, new_losers=False):
    self.players = new_players
    self.seeds = new_seeds
    self.initial_skill = (-1, -1)
    if (self.players[0] != None):
      self.initial_skill = self.players[0].skill
    if (self.players[1] != None):
      self.initial_skill = self.players[1].skill

    self.winner_to = new_winner_to
    self.loser_to = new_loser_to
    self.match_from = [None, None]

    self.round = new_round
    self.losers = new_losers

    self.p_players = [{}, {}]

  # Calculate the probabilities of players reaching the current match
  def CalculatePlayerProbabilities(self, conflicts):
    e_conflicts, e_importance = 0.0, 0.0
    self.p_players = [{}, {}]
    if self.match_from[0] == None:
      self.p_players[0][self.players[0]] = 1.0
      self.p_players[1][self.players[1]] = 1.0
    else:
      # Loop over matches leading into this one and determine who advances/falls to losers.
      for prev_index in xrange(0, 2):
        prev_match = self.match_from[prev_index]
        for side in xrange(0, 2):
          for player, p1 in prev_match.p_players[side].iteritems():
            p = 0.0
            for opponent, p2 in prev_match.p_players[1-side].iteritems():
              p += p1 * p2 * player.p_win(opponent)
              if prev_match.losers == self.losers and \
                 player.region == opponent.region and not player.name == opponent.name:
                e_conflicts += p1 * p2 / 2
                conflict = annealing.BracketConflict(prev_match, player, opponent, p1 * p2,
                                                     prev_match.round, prev_match.losers)
                conflicts.AddConflict(conflict)
                e_importance += conflict.importance / 2

            # Add the probabilities to the dict for this match.
            if self.losers and not prev_match.losers:
              if p1-p > 0:
                self.p_players[prev_index][player] = p1-p
            elif p > 0:
              # Special case: a player reaches a match from winners and losers.
              if player in self.p_players[prev_index]:
                self.p_players[prev_index][player] += p
              else:
                self.p_players[prev_index][player] = p
    return e_conflicts, e_importance

  # String output functions.
  def PrettyString(self, depth=0, spaces_per_round=0):
    return " "*(spaces_per_round*depth) + str(self.seeds[0]) + " " + self.players[0].name + "\n" + \
           " "*(spaces_per_round*depth) + str(self.seeds[1]) + " " + self.players[1].name

  def ProbabilityString(self, depth=0, spaces_per_round=0):
    return " "*(spaces_per_round*depth) + self.PrettifyProbMap(self.p_players[0]) + "\n" + \
           " "*(spaces_per_round*depth) + self.PrettifyProbMap(self.p_players[1])

  def PrettifyProbMap(self, map):
    count = len(map) - 1
    str_out = "{"
    for player, p in map.iteritems():
      str_out += player.name + ": " + str(p)
      if count > 0:
        str_out += ", "
      count -= 1
    return str_out + "}"

  def __repr__(self):
    return str(self.seeds[0]) + " " + self.players[0].name + " vs " + \
           str(self.seeds[1]) + " " + self.players[1].name

# Map for holding the players by skill level.
class PlayerMap:
  def __init__(self):
    self.player_list = []
    self.skill_map = {}

  def AddPlayer(self, player):
    self.player_list.append(player)
    if player.skill not in self.skill_map:
      self.skill_map[player.skill] = []
    self.skill_map[player.skill].append(player)

  def AddPlayerRaw(self, name, skill, region):
    player = Player(name, int(skill), region)
    self.AddPlayer(player)

  def GetPlayersBySkill(self):
    keys = self.skill_map.keys()
    keys.sort(reverse=True)
    players_out = []
    for key in keys:
      players_out.extend(self.skill_map[key])
    return players_out

  def GetPlayersWithinSkill(self, skill, range):
    players_out = []
    for key in self.skill_map.keys():
      if key <= skill + range and key >= skill - range:
        players_out.extend(self.skill_map[key])
    return players_out

  def GetRandomPlayerWithinSkill(self, skill, range):
    size = 0
    for key in self.skill_map.keys():
      if key <= skill + range and key >= skill - range:
        size += len(self.skill_map[key])

    if size < 2:
      return None

    rnd = random.randint(0, size - 1)
    for key in self.skill_map.keys():
      if key <= skill + range and key >= skill - range:
        players = self.skill_map[key]
        size = len(players)
        if rnd < size:
          return players[rnd]
        else:
          rnd -= size
    return None

  def PadWithByes(self):
    current = len(self.player_list)
    if current <= 2:
      return
    target = 1<<(current-1).bit_length()
    for i in xrange(1, target - current + 1):
      self.AddPlayer(Player(new_name="bye"+str(i), new_is_bye=True))

  def GetPlayersString(self):
    str_out = ""
    for player in self.player_list:
      str_out += str(player) + "\n"
    return str_out

  def GetPlayersBySkillString(self):
    str_out = ""
    for player in self.GetPlayersBySkill():
      str_out += str(player) + "\n"
    return str_out
