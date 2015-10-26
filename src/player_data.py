import random

import annealing

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

  def GetPlayersWithinSkill(self, skill, range, pool_num):
    players_out = []
    for key in self.skill_map.keys():
      if key <= skill + range and key >= skill - range:
        for player in self.skill_map[key]:
          if player.pool_num == pool_num:
            players_out.append(player)
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
