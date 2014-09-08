import re
from glob import glob
from xml import etree

def run(filename):
  return interp(parse(filename))

def parse(filename):
  with open(filename, 'r') as f:
    tree = etree.XML(f.read())

  unparsed_commands = [command.text for command in tree.findall('.//annotation')]

  PATTERN = re.compile(r'''((?:[^\,"']|"[^"]*"|'[^']*')+)''')

  commands = []
  for unparsed_command in unparsed_commands:
    command_name, unparsed_command = unparsed_command.split('(', 1)

    unparsed_command = unparsed_command.rstrip(')')

    arguments = PATTERN.split(unparsed_command)[1::2]

    arguments = [arg.replace('"', '').strip() for arg in arguments]

    if arguments[0].startswith('{'):
      end = (i for i, v in enumerate(arguments) if v.endswith('}')).next()
      arguments = [{arg.lstrip('{').rstrip('}') for arg in arguments[0:end + 1]}] + arguments[end + 1:]

    arguments = [None if arg == "null" else arg for arg in arguments]

    commands.append((command_name, arguments))

  return commands

def interp(commands):
  w = WorldState()
  states = [w]
  for command in commands:
    w = getattr(w, command[0])(*command[1])
    states.append(w)

  return states

class RecipeException(Exception):
  pass

class IngredientExistsException(RecipeException):
  pass

class IngredientNonExistsException(RecipeException):
  pass

class ToolExistsException(RecipeException):
  pass

class ToolNonExistsException(RecipeException):
  pass

class ContainNonExistsException(RecipeException):
  pass

class NullException(RecipeException):
  pass

class WorldState(object):

  def __init__(self, I = set(), T = set(), I_d = {}, T_d = {}, C = {}):
    self.I = I
    self.T = T
    self.I_d = I_d
    self.T_d = T_d
    self.C = C

  def __ingredient_exists(self, ingredient):
    return ingredient in self.I or ingredient in self.I_d.keys()

  def __tool_exists(self, tool):
    return tool in self.T or tool in self.T_d.keys()

  def __is_null(self, value):
    return value is None or value == ""

  def create_ing(self, ingredient, description):
    if self.__is_null(ingredient):
      raise NullException("create_ing: ingredient must not be null")

    if self.__is_null(description):
      raise NullException("create_ing: description must not be null")

    if self.__ingredient_exists(ingredient):
      raise IngredientExistsException("create_ing: ingredient must not already exist: " + str(ingredient))

    I_d = dict(self.I_d)
    I_d[ingredient] = description

    return WorldState(self.I | {ingredient},
                      self.T,
                      I_d,
                      self.T_d,
                      self.C)

  def create_tool(self, tool, description):
    if self.__is_null(tool):
      raise NullException("create_tool: tool must not be null")

    if self.__is_null(description):
      raise NullException("create_tool: description must not be null")

    if self.__tool_exists(tool):
      raise ToolExistsException("create_tool: tool must not already exist: " + str(tool))

    T_d = dict(self.T_d)
    T_d[tool] = description

    return WorldState(self.I,
                      self.T | {tool},
                      self.I_d,
                      T_d,
                      self.C)

  def combine(self, ingredients, ingredient, description, manner):
    w = self
    for i in ingredients:
      w = self.serve(i, None)

    return w.create_ing(ingredient, description)

  def separate(self, ingredient, out1, out1desc, out2, out2desc, manner):
    return self.serve(ingredient, None).create_ing(out1, out1desc).create_ing(out2, out2desc)

  def put(self, ingredient, tool):
    if self.__is_null(ingredient):
      raise NullException("put: ingredient must not be null")

    if self.__is_null(tool):
      raise NullException("put: tool must not be null")

    if not self.__ingredient_exists(ingredient):
      raise IngredientNonExistsException("put: ingredient must already exist: " + str(ingredient))

    if not self.__tool_exists(tool):
      raise ToolNonExistsException("put: tool must already exist: " + str(tool))

    C = dict(self.C)
    C[tool] = ingredient

    return WorldState(self.I,
                      self.T,
                      self.I_d,
                      self.T_d,
                      C)


  def remove(self, ingredient, tool):
    if self.__is_null(ingredient):
      raise NullException("remove: ingredient must not be null: " + str(ingredient))

    if self.__is_null(tool):
      raise NullException("remove: tool must not be null: " + str(tool))

    if not self.__ingredient_exists(ingredient):
      raise IngredientNonExistsException("remove: ingredient must already exist: " + str(ingredient))

    if not self.__tool_exists(tool):
      raise ToolNonExistsException("remove: tool must already exist: " + str(tool))

    if not (tool in self.C.keys() and ingredient == self.C[tool]):
      raise ContainNonExistsException("remove: ingredient must be in tool: " + str((tool, ingredient)))

    return WorldState(self.I,
                      self.T,
                      self.I_d,
                      self.T_d,
                      {k: v for k, v in self.C.items() if k != tool})

  def do(self, ingredient, tool, out, outdesc, manner):
    return self.serve(ingredient, None).create_ing(out, outdesc)

  def cut(self, ingredient, tool, out, outdesc, manner):
    return self.do(ingredient, tool, out, outdesc, manner)

  def mix(self, ingredient, tool, out, outdesc, manner):
    return self.do(ingredient, tool, out, outdesc, manner)

  def cook(self, ingredient, tool, out, outdesc, manner):
    return self.do(ingredient, tool, out, outdesc, manner)

  def serve(self, ingredient, manner):
    if self.__is_null(ingredient):
      raise NullException("serve: ingredient must not be null")

    if not self.__ingredient_exists(ingredient):
      raise IngredientNonExistsException("serve: ingredient must already exist: " + str(ingredient))

    return WorldState(self.I - {ingredient},
                      self.T,
                      {k: v for k, v in self.I_d.items() if k != ingredient},
                      self.T_d,
                      self.C)

  def set(self, *_):
    return self

  def leave(self, *_):
    return self

  def chefcheck(self, *_):
    return self


good = 0
bad = 0
for recipe_name in glob('annotated_recipes/*.xml'):
  try:
    run(recipe_name)
    good += 1
    print recipe_name, 'was successfully evaluated!'
  except RecipeException, e:
    bad += 1
    print recipe_name, 'was unsuccessfully evaluted with the following exception:'
    print e
  except TypeError, e:
    bad += 1
    print recipe_name, 'was unsuccessfully evaluted with the following exception:'
    print e
  print ''

print 'Successful evaluations:', good
print 'Unsuccessful evaluations:', bad
print 'Total evaluations:', good + bad