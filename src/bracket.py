import classes
import util
import random
import annealing

# Bracket class.
class Bracket:
  def __init__(self, config):
    self.config = config
    self.players = []
    self.rounds = -1
    self.matches = []
    self.losers_matches = []
    self.root = None
    self.num_players = -1

  # Build and seed a bracket.
  def BuildBracket(self, player_map):
    self.player_map = player_map
    self.players = player_map.GetPlayersBySkill()
    self.num_players = len(self.players)
    if self.num_players < 2:
      return
    self.BuildWinnersBracket()
    self.BuildLosersBracket()

  # Build winners bracket.
  def BuildWinnersBracket(self):
    self.rounds = (self.num_players-1).bit_length()
    self.root = classes.BracketMatch([self.players[0], self.players[1]], (1, 2), None, None, self.rounds, False)
    self.matches.append([self.root])

    for round in xrange(1, self.rounds):
      round_matches = [None] * (1<<round)
      for match in xrange(0, 1<<round):
        next_match = self.matches[0][match/2]
        opponent_seed = self.GetOpponent(next_match, match%2, 1<<(round+1))
        round_matches[match] = classes.BracketMatch([next_match.players[match%2], self.players[opponent_seed]],
                                                    (next_match.seeds[match%2], opponent_seed+1),
                                                    next_match, None, self.rounds - round, False)
        next_match.match_from[match%2] = round_matches[match]

      self.matches.insert(0, round_matches)
      self.DoCurrentRoundRegionalSeeding()

  # Build losers bracket.
  def BuildLosersBracket(self):
    self.losers_rounds = 2*(self.rounds-1)
    for round in xrange(0, self.losers_rounds):
      num_matches = self.num_players/(1<<(round/2 + 2))
      round_matches = [None] * num_matches
      for match in xrange(0, num_matches):
        match1, match2 = None, None
        # Special case, bring both players down from winners
        if round == 0:
          match1 = self.matches[0][2*match]
          match2 = self.matches[0][2*match + 1]
          round_matches[match] = classes.BracketMatch([match2.players[1], match1.players[1]],
                                                      (match2.seeds[1], match1.seeds[1]), None, None, round, True)
          match1.loser_to = round_matches[match]
          match2.loser_to = round_matches[match]
        # Advance the round in losers
        elif round % 2 == 0:
          match1 = self.losers_matches[round-1][2*match]
          match2 = self.losers_matches[round-1][2*match + 1]
          round_matches[match] = classes.BracketMatch([match1.players[0], match2.players[0]],
                                                      (match1.seeds[0], match2.seeds[0]), None, None, round, True)
          match1.winner_to = round_matches[match]
          match2.winner_to = round_matches[match]
        # Bring down players from winners
        else:
          match1 = self.GetScrambledMatch(round, num_matches, match)
          match2 = self.losers_matches[round-1][match]
          round_matches[match] = classes.BracketMatch([match1.players[1], match2.players[0]],
                                                      (match1.seeds[1], match2.seeds[0]), None, None, round, True)
          match1.loser_to = round_matches[match]
          match2.winner_to = round_matches[match]
        round_matches[match].match_from = [match1, match2]

      self.losers_root = round_matches[0]
      self.losers_matches.append(round_matches)

  # Do the regional seeding for the current round of winners bracket.
  def DoCurrentRoundRegionalSeeding(self):
    # Find a match with players from the same region.
    for match in self.matches[0]:
      if not match.players[0].region == match.players[1].region:
        continue

      # Search for eligible swaps.
      skill_diff, closest_match, index = self.GetEligibleMatch(match)
      skill_diff2, closest_player = self.GetEligiblePlayer(match)

      # If a match was found, swap the lower seeded players in the matches.
      if not closest_match == None and (closest_player == None or skill_diff <= skill_diff2):
        print "Swapping " + str(match.seeds[1]) + " " + match.players[1].name + " with " + \
              str(closest_match.seeds[index]) + " " + closest_match.players[index].name
        self.players[match.seeds[1]-1], self.players[closest_match.seeds[index]-1] = \
          self.players[closest_match.seeds[index]-1], self.players[match.seeds[1]-1]
        match.players[1], closest_match.players[index] = closest_match.players[index], match.players[1]
      # Otherwise, swap that player with the lower seeded player in the bracket.
      elif not closest_player == None:
        print self.GetWinnersBracketString()
        print "Swapping players " + str(match.seeds[1]) + " " + match.players[1].name + " with " + \
              closest_player.name
        i = 0
        while i < len(self.players) and not self.players[i].name == closest_player.name:
          i += 1
        i2 = match.seeds[1]-1
        self.players[match.seeds[1]-1], self.players[i] = \
          self.players[i], self.players[match.seeds[1]-1]
        match.players[1] = closest_player
        print self.GetWinnersBracketString()

  # Search for another match in the current round that would be eligible to swap.
  def GetEligibleMatch(self, match):
    skill_diff = -1
    closest_match = None
    for new_match in self.matches[0]:
      if not new_match.players[1].is_bye:
        for i in xrange(1, -1, -1):
          new_skill_diff = abs(match.players[1].skill - new_match.players[i].skill)
          if not new_match.players[i].region == match.players[1].region and \
             not new_match.players[1-i].region == match.players[1].region and \
             new_skill_diff <= self.config["tolerance"] and (skill_diff == -1 or skill_diff > new_skill_diff):
            closest_match = new_match
            skill_diff = new_skill_diff
            index = i

    return skill_diff, closest_match, index

  # Search for an eligible player to swap with.
  def GetEligiblePlayer(self, match):
    skill_diff = -1
    closest_player = None
    for new_player in self.player_map.GetPlayersWithinSkill(match.players[1].skill, self.config["tolerance"]):
      new_skill_diff = abs(match.players[1].skill - new_player.skill)
      if not new_player.is_bye and \
         not new_player.region == match.players[1].region and \
         new_skill_diff <= self.config["tolerance"] and (skill_diff == -1 or skill_diff > new_skill_diff):
        closest_player = new_player
        skill_diff = new_skill_diff

    return skill_diff, closest_player

  # Simulate the bracket and calculate the number of conflicts.
  def SimulateBracket(self, param, new_players):
    if not new_players == None:
      self.LoadSeeds(new_players)
    e_conflicts, e_importance = 0.0, 0.0
    conflicts = annealing.ConflictSet()
    for arr in [self.matches, self.losers_matches]:
      for round in arr:
        for match in round:
          incrementals = match.CalculatePlayerProbabilities(conflicts)
          e_conflicts += incrementals[0]
          e_importance += incrementals[1]
    return e_conflicts, e_importance, conflicts

  def SaveSeeds(self):
    seeds = []
    for match in self.matches[0]:
      for player in match.players:
        seeds.append(player)
    error = False
    for i in xrange(0, len(self.players)-1):
      for j in xrange(i+1, len(self.players)):
        if self.players[i] == self.players[j]:
          print "ERROR", self.players[i], self.players[j]
          print self.players
          error = True
    if error:
      None.hi
    return seeds

  def LoadSeeds(self, new_seeds):
    self.players = list(new_seeds)
    i = 0
    for match in self.matches[0]:
      for j in xrange(0, 2):
        match.players[j] = new_seeds[i]
        i += 1

  def GetAnnealingInit(self):
    return list(self.players), self.SaveSeeds()

  # Seeding util functions
  def GetOpponent(self, bracket_match, player, bracket_size):
    return bracket_size - bracket_match.seeds[player]

  def GetScrambledMatch(self, round, round_size, index):
    scramble_type = (round-1)/2 % 4
    winners_round = (round-1)/2 + 1

    if scramble_type == 0:    # r
      return self.matches[winners_round][round_size - index - 1]
    elif scramble_type == 1:  # rs
      return self.matches[winners_round][(round_size/2 - index - 1) % round_size]
    elif scramble_type == 2:  # ns
      return self.matches[winners_round][(index + round_size/2) % round_size]
    elif scramble_type == 3:  # n
      return self.matches[winners_round][index]
    # Impossible
    return None

  # Print utils
  def GetBracketString(self):
    return self.GetWinnersBracketString(0) + "\n" + ("-"*60) + "\n" + self.GetLosersBracketString(0)

  def GetProbabilisticBracketString(self):
    return self.GetWinnersBracketString(1) + "\n" + ("-"*60) + "\n" + self.GetLosersBracketString(1)

  def GetWinnersBracketString(self, type=0):
    return self.BracketStringHelper(self.root, 1, self.rounds, type)

  def GetLosersBracketString(self, type=0):
    return self.BracketStringHelper(self.losers_root, 1, self.losers_rounds, type)

  def BracketStringHelper(self, cur, depth, rounds, type):
    str_out = ""
    if not cur.match_from[0] == None and cur.losers == cur.match_from[0].losers:
      str_out += self.BracketStringHelper(cur.match_from[0], depth + 1, rounds, type)

    if type == 0:
      str_out += cur.PrettyString(rounds - depth, self.config["num_spaces_per_round"]) + "\n"
    elif type == 1:
      str_out += cur.ProbabilityString(rounds - depth, self.config["num_spaces_per_round"]) + "\n"

    if not cur.match_from[1] == None and cur.losers == cur.match_from[1].losers:
      str_out += self.BracketStringHelper(cur.match_from[1], depth + 1, rounds, type)
    return str_out

  def GetPlayersBySeedString(self):
    str_out = ""
    for player in self.players:
      str_out += player.name + "\n"
    return str_out
