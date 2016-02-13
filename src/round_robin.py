import interfaces

class RoundRobinPool(interfaces.Pool):
  def __init__(self, config, players):
    self.config = config
    self.players = list(players)
    self.num_players = len(players)

  def SetSeeds(self, seeds):
    self.players = list(seeds)
    self.num_players = len(self.players)

  def GetSeeds(self):
    return list(self.players)

  def GetSortedSeeds(self):
    return list(self.players)

  def Simulate(self, conflicts):
    for i in xrange(0, self.num_players - 1):
      for j in xrange(i + 1, self.num_players):
        if not self.players[i].is_bye and not self.players[j].is_bye and \
           self.players[i].region == self.players[j].region and \
           not self.players[i].name == self.players[j].name:
          conflicts.AddConflict(RoundRobinConflict(self.players[i], self.players[j]))

# Pool conflict struct.
class RoundRobinConflict(interfaces.Conflict):
  def __init__(self, player1, player2):
    self.player1 = player1
    self.player2 = player2
    self.score = self.CalculateScore()
    self.p = 1.0

  def CalculateScore(self):
    return self.player1.skill * self.player2.skill / 100.0

  def __lt__(self, other):
    if not isinstance(other, RoundRobinConflict):
      return 0
    elif not self.score == other.score:
      return self.score < other.score
    elif not self.player1 == other.player1:
      return self.player1 < other.player1
    elif not self.player2 == other.player2:
      return self.player2 < other.player2
    return 1
    
  def __hash__(self):
    return hash(tuple(sorted([self.player1.name, self.player2.name])))

  def __eq__(self, other):
    return not other == None and self.player1 == other.player1 and self.player2 == other.player2 or \
           self.player1 == other.player2 and self.player2 == other.player1

  def __str__(self):
    return self.player1.name + ", " + self.player2.name + "\nscore = " + str(self.score)

  def __repr__(self):
    return self.__str__()

if __name__ == "__main__":
  print "Run main.py"
