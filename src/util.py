import os
import sys

# Pool type enum
class PoolType:
  BRACKET = 1
  ROUND_ROBIN = 2

# Load functions.
def ParseConfigLine(line, config_types):
  split_line = line.split()
  for i in xrange(len(split_line)):
    split_line[i] = split_line[i].strip()
  split_line = filter(None, split_line)
  if not len(split_line) == 2:
    return (None, None)

  field = split_line[0].strip()
  value = split_line[1].strip()
  if field not in config_types or config_types[field] == 'string':
    return (field, value)
  elif config_types[field] == 'int':
    return (field, int(value))
  elif config_types[field] == 'float':
    return (field, float(value))
  elif config_types[field] == 'bool':
    return (field, bool(value))
  else:
    return (None, None)

def LoadConfig(config, config_types):
  try:
    with open(config["config_file"]) as f:
      line_num = 1
      for line in f:
        if not IsCommentLine(line):
          try:
            field, value = ParseConfigLine(line, config_types)
            if not field == None and not value == None:
              print "Found config setting: " + field + ": \"" + str(value) + "\" " + str(type(value))
              config[field] = value
            else:
              print "Skipping config line:", line_num
          except ValueError:
            print "Could not parse config line:", line_num
        line_num += 1
    print "Loaded config settings"
    print "-"*60
  except IOError:
    print "No config file found. Using default configuration"

def LoadPlayers(config, player_map):
  try:
    with open(config["player_in_file"]) as f:
      line_num = 1
      for line in f:
        if not IsCommentLine(line):
          split_line = line.split(",")
          for i in xrange(len(split_line)):
            split_line[i] = split_line[i].strip()
          split_line = filter(None, split_line)

          if len(split_line) == 3:
            try:
              player_map.AddPlayerRaw(split_line[0], split_line[1], split_line[2])
              print "Found player: " + split_line[0] + ", " + split_line[1] + ", " + split_line[2]
            except ValueError:
              print "Count not parse player line:", line_num
          else:
            print "Skipping player line:", line_num
            print split_line
        line_num += 1
    print "Loaded player data"
  except IOError:
    print "No player data file found. Exiting."
    sys.exit(0)

def IsCommentLine(line):
  return len(line.lstrip()) > 0 and line.lstrip()[0] == '#'
    
# Output functions.
def PrintStr(param):
  print param[0]

def WriteStr(param):
  if not len(param) == 2:
    print "Write error: Incorrect number of params."
    return
  str_out, filepath = param[0], param[1]
  if filepath == None:
    print "Write error: No filepath."
    return
  try:
    if not os.path.exists(os.path.dirname(filepath)):
      os.makedirs(os.path.dirname(filepath))
    with open(filepath, "w") as f:
      f.write(str_out)
    print "Wrote to: " + filepath
  except IOError:
    print "Write error: File not found: " + filepath + " Skipping."

if __name__ == "__main__":
  print "Run seeding.py"
