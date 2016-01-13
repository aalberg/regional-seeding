# General interfaces for annealing
class Pool:
  def __init__(self, config, players):
    pass

  def SetSeeds(self, seeds):
    raise Exception("Pool.SetSeeds")

  def GetSeeds(self):
    raise Exception("Pool.GetSeeds")

  def GetSortedSeeds(self):
    raise Exception("Pool.GetSortedSeeds")

  def Simulate(self):
    raise Exception("Pool.Simulate")

class Conflict:
  def __init__(self):
    self.player1 = None
    self.player2 = None
    self.score = 0.0
    self.p = 0.0

  def CalculateScore(self):
    raise Exception("Conflict.CalculateScore")
