import interfaces

class RoundRobinPool(interfaces.Pool):
  def __init__(self, config, players):
    self.config = config
    self.players = list(players)
    self.num_players = len(players)

  def SetSeeds(self, seeds):
    self.players = list(seeds)
    self.num_players = len(players)

  def GetSeeds(self):
    return list(players)

  def GetSortedSeeds(self):
    return list(players)

  def Simulate(self, conflicts):
    for i in xrange(0, size - 1):
      for j in xrange(i + 1, size):
        if self.players[i].region == self.players[j] and not self.players[i].name == self.players[j].name:
          conflicts.AddConflict(RoundRobinConflict(self.players[i], self.players[j]))

# Pool conflict struct.
class RoundRobinConflict(interfaces.Conflict):
  def __init__(self, player1, player2):
    self.player1 = player1
    self.player2 = player2
    self.score = self.CalculateScore()
    self.p = 1.0

  def CalculateScore(self):
    return 1

  def __hash__(self):
    return hash(tuple(sorted([self.player1.name, self.player2.name])))

  def __eq__(self, other):
    return self.player1 == other.player1 and self.player2 == other.player2 or \
           self.player1 == other.player2 and self.player2 == other.player1

  def __str__(self):
    return self.player1.name + ", " + self.player2.name + "\nscore = " + str(self.score)

  def __repr__(self):
    return self.__str__()