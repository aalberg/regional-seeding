import interfaces

# Bracket class.
class BracketPool(interfaces.Pool):
  def __init__(self, config, players):
    self.config = config
    self.players = players
    self.num_players = len(self.players)
    self.rounds = -1
    self.matches = []
    self.losers_matches = []
    self.root = None

    self.BuildBracket()

  # Build and seed a bracket.
  def BuildBracket(self):
    if self.num_players < 2:
      return
    self.BuildWinnersBracket()
    self.BuildLosersBracket()

  # Build winners bracket.
  def BuildWinnersBracket(self):
    self.rounds = (self.num_players-1).bit_length()
    self.root = BracketMatch([self.players[0], self.players[1]], (1, 2), None, None, self.rounds, False)
    self.matches.append([self.root])

    for round in xrange(1, self.rounds):
      round_matches = [None] * (1<<round)
      for match in xrange(0, 1<<round):
        next_match = self.matches[0][match/2]
        opponent_seed = self.GetOpponent(next_match, match%2, 1<<(round+1))
        round_matches[match] = BracketMatch([next_match.players[match%2], self.players[opponent_seed]],
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
          round_matches[match] = BracketMatch([match2.players[1], match1.players[1]],
                                                      (match2.seeds[1], match1.seeds[1]), None, None, round, True)
          match1.loser_to = round_matches[match]
          match2.loser_to = round_matches[match]
        # Advance the round in losers
        elif round % 2 == 0:
          match1 = self.losers_matches[round-1][2*match]
          match2 = self.losers_matches[round-1][2*match + 1]
          round_matches[match] = BracketMatch([match1.players[0], match2.players[0]],
                                                      (match1.seeds[0], match2.seeds[0]), None, None, round, True)
          match1.winner_to = round_matches[match]
          match2.winner_to = round_matches[match]
        # Bring down players from winners
        else:
          match1 = self.GetScrambledMatch(round, num_matches, match)
          match2 = self.losers_matches[round-1][match]
          round_matches[match] = BracketMatch([match1.players[1], match2.players[0]],
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
    index = -1
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
    for new_player in self.players:
      new_skill_diff = abs(match.players[1].skill - new_player.skill)
      if not new_player.is_bye and \
         not new_player.region == match.players[1].region and \
         new_skill_diff <= self.config["tolerance"] and (skill_diff == -1 or skill_diff > new_skill_diff):
        closest_player = new_player
        skill_diff = new_skill_diff

    return skill_diff, closest_player

  # Load/save the current seeding.
  def SetSeeds(self, new_seeds):
    self.players = list(new_seeds)
    i = 0
    for match in self.matches[0]:
      for j in xrange(0, 2):
        match.players[j] = new_seeds[i]
        i += 1

  def GetSeeds(self):
    seeds = []
    for match in self.matches[0]:
      for player in match.players:
        seeds.append(player)
    return seeds

  def GetSortedSeeds(self):
    return list(self.players)

  # Simulate the bracket and calculate the number of conflicts.
  def Simulate(self, conflicts):
    for arr in [self.matches, self.losers_matches]:
      for round in arr:
        for match in round:
          match.CalculatePlayerProbabilities(conflicts)

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
  def GetPoolString(self):
    return self.GetWinnersBracketString(0) + "\n" + ("-"*60) + "\n" + self.GetLosersBracketString(0)

  def GetDebugString(self):
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
    e_conflicts, e_score = 0.0, 0.0
    self.p_players = [{}, {}]
    if self.match_from[0] == None:
      self.p_players[0][self.players[0]] = 1.0
      self.p_players[1][self.players[1]] = 1.0
    else:
      # Loop over matches leading into this one and determine who advances/falls to losers.
      for prev_index in xrange(0, 2):
        prev_match = self.match_from[prev_index]
        if self.losers and not prev_match.losers:
          self.players[prev_index] = prev_match.players[1]
        else:
          self.players[prev_index] = prev_match.players[0]
        for side in xrange(0, 2):
          for player, p1 in prev_match.p_players[side].iteritems():
            p = 0.0
            for opponent, p2 in prev_match.p_players[1-side].iteritems():
              p += p1 * p2 * player.p_win(opponent)
              if prev_match.losers == self.losers and \
                 not player.is_bye and not opponent.is_bye and \
                 player.region == opponent.region and not player.name == opponent.name:
                e_conflicts += p1 * p2 / 2
                conflict = BracketConflict(prev_match, player, opponent, p1 * p2,
                                           prev_match.round, prev_match.losers)
                conflicts.AddConflict(conflict)
                e_score += conflict.score / 2

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
    return e_conflicts, e_score

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

# Bracket conflict struct.
class BracketConflict(interfaces.Conflict):
  def __init__(self, match, player1, player2, p, round, losers=False):
    self.match = match
    self.p_map = match.p_players
    self.player1 = player1
    self.player2 = player2
    self.p = p
    self.round = round
    self.losers = losers
    self.score = self.Calculatescore()

  def Calculatescore(self):
    return self.p / ((self.round + 1)**2)
    
  def __lt__(self, other):
    if isinstance(other, BracketConflict):
      return 0
    elif not self.score == other.score:
      return self.score < other.score
    elif not self.p == other.p:
      return self.p < other.p
    elif not self.round == other.round:
      return self.round < other.round
    elif not self.player1 == other.player1:
      return self.player1 < other.player1
    elif not self.player2 == other.player2:
      return self.player2 < other.player2
    return 1
      
  def __hash__(self):
    return hash((tuple(sorted([self.player1.name, self.player2.name])), self.round, self.losers))

  def __eq__(self, other):
    return not other == None and self.match == other.match and \
           (self.player1 == other.player1 and self.player2 == other.player2 or \
           self.player1 == other.player2 and self.player2 == other.player1)

  def __str__(self):
    str_out = ""
    if self.losers:
      str_out += "Losers"
    else:
      str_out += "Winners"
    str_out += " round " + str(self.round) + "\n" + self.player1.name + ", " + self.player2.name + \
               "\np = " + str(self.p) + "\nscore = " + str(self.score) + "\n" + \
               self.match.PrettifyProbMap(self.p_map[0]) + "\n" + self.match.PrettifyProbMap(self.p_map[1])
    return str_out

  def __repr__(self):
    return self.__str__()

if __name__ == "__main__":
  print "Run main.py"
