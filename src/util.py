import os

# Pool type enum
class PoolType:
  BRACKET = 1
  ROUND_ROBIN = 2

# Load functions.
def ParseConfigLine(line, config_types):
  split_line = line.split(' ', 1)
  field = split_line[0]
  value = split_line[1]
  if field not in config_types or config_types[field] == 'string':
    return (field, value)
  elif config_types[field] == 'int':
    return (field, int(value))
  elif config_types[field] == 'float':
    return (field, float(value))
  elif config_types[field] == 'bool':
    return (field, bool(value))

def LoadConfig(config, config_types):
  try:
    with open(config["config_file"]) as f:
      for line in f:
        line = line.rstrip()
        if len(line) <= 2:
          continue
        field, value = ParseConfigLine(line, config_types)
        print "Found config setting: " + field + ": \"" + str(value) + "\" " + str(type(value))
        config[field] = value
    print "Loaded config settings"
  except IOError:
    print "No config file found. Using default configuration"

def LoadPlayers(config, player_map):
  try:
    with open(config["player_in_file"]) as f:
      for line in f:
        line = line.rstrip()
        if len(line) <= 2:
          continue
        split_line = line.split(",", 2)
        if len(split_line) == 1:
          split_line.extend(["-1", ""])
        elif len(split_line) == 2:
          split_line.append("")
        print "Found player: " + split_line[0] + ", " + split_line[1] + ", " + split_line[2]
        player_map.AddPlayerRaw(split_line[0], split_line[1], split_line[2])
    print "Loaded player data"
  except IOError:
    print "No player data file found. Exiting."
    sys.exit(0)

# Output functions.
def PrintStr(param):
  print param[0]

def WriteStr(param):
  str_out, filepath = param[0], param[1]
  if filepath == None:
    return
  try:
    if not os.path.exists(os.path.dirname(filepath)):
      os.makedirs(os.path.dirname(filepath))
    with open(filepath, "w") as f:
      f.write(str_out)
    print "Wrote to: " + filepath
  except IOError:
    print "File not found: " + filepath + " Skipping."

if __name__ == "__main__":
  print "Run seeding.py"
