# CURD Recipe Evaluator

# Written by Frank Goodman (fgoodman)
# 9/7/14

# Usage (parsing):
# parse('recipe_file.xml')

# Usage (evaluating):
# interp(parse('recipe_file.xml'))

from glob import glob
from inspect import stack
from lxml import etree
from re import compile

def run(filename):
  return interp(parse(filename))

def parse(filename):
  with open(filename, 'r') as f:
    tree = etree.XML(f.read())

  unparsed_commands = [command.text for command in tree.findall('.//annotation')]

  PATTERN = compile(r'''((?:[^\,"']|"[^"]*"|'[^']*')+)''')

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

  def __init__(self, message):

    Exception.__init__(self, "%s: %s" % (stack()[2][3], message))

class WorldState(object):

  # Structure of the world's state

  def __init__(self, I_d = {}, T_d = {}, C = {}):
    self.I_d = I_d
    self.T_d = T_d
    self.C = C

  # Predicates for safety checks

  def __IsNull(self, value):
    return value is None or value == "" or value == "null"

  def __IsIngredient(self, ingredient):
    return ingredient in self.I_d.keys()

  def __IsTool(self, tool):
    return tool in self.T_d.keys()

  def __IsContain(self, ingredient, tool):
    return tool in self.C.keys() and ingredient == self.C[tool]

  # Desugared CURD

  def __AddIngredient(self, ingredient, description):
    if self.__IsNull(ingredient):
      raise RecipeException("Ingredient must not be null.")

    if self.__IsNull(description):
      raise RecipeException("Description must not be null.")

    if self.__IsIngredient(ingredient):
      raise RecipeException("Ingredient '%s' must not already exist." % ingredient)

    I_d = dict(self.I_d)
    I_d[ingredient] = description

    return WorldState(I_d, self.T_d, self.C)

  def __RemoveIngredient(self, ingredient):
    if self.__IsNull(ingredient):
      raise RecipeException("Ingredient must not be null.")

    if not self.__IsIngredient(ingredient):
      raise RecipeException("Ingredient '%s' must already exist." % ingredient)

    I_d = dict(self.I_d)
    del I_d[ingredient]

    return WorldState(I_d, self.T_d, self.C)

  def __AddTool(self, tool, description):
    if self.__IsNull(tool):
      raise RecipeException("Tool must not be null.")

    if self.__IsNull(description):
      raise RecipeException("Description must not be null.")

    if self.__IsTool(tool):
      raise RecipeException("Tool '%s' must not already exist." % tool)

    T_d = dict(self.T_d)
    T_d[tool] = description

    return WorldState(self.I_d, T_d, self.C)

  def __AddContain(self, ingredient, tool):
    if self.__IsNull(ingredient):
      raise RecipeException("Ingredient must not be null.")

    if self.__IsNull(tool):
      raise RecipeException("Tool must not be null.")

    if not self.__IsIngredient(ingredient):
      raise RecipeException("Ingredient '%s' must already exist." % ingredient)

    if not self.__IsTool(tool):
      raise RecipeException("Tool '%s' must already exist." % tool)

    if self.__IsContain(ingredient, tool):
      raise RecipeException("Contain '(%s, %s)' must not already exist." % (tool, ingredient))

    C = dict(self.C)
    C[tool] = ingredient

    return WorldState(self.I_d, self.T_d, C)

  def __RemoveContain(self, ingredient, tool):
    if self.__IsNull(ingredient):
      raise RecipeException("Ingredient must not be null.")

    if self.__IsNull(tool):
      raise RecipeException("Tool must not be null.")

    if not self.__IsIngredient(ingredient):
      raise RecipeException("Ingredient '%s' must already exist." % ingredient)

    if not self.__IsTool(tool):
      raise RecipeException("Tool '%s' must already exist." % tool)

    if not self.__IsContain(ingredient, tool):
      raise RecipeException("Contain '(%s, %s)' must already exist." % (tool, ingredient))

    C = dict(self.C)
    del C[tool]

    return WorldState(self.I_d, self.T_d, C)

  # CURD

  def create_ing(self, ingredient, description):
    return self.__AddIngredient(ingredient, description)

  def create_tool(self, tool, description):
    return self.__AddTool(tool, description)

  def combine(self, ingredients, ingredient, description, manner):
    return reduce(lambda s, i: s.__RemoveIngredient(i), ingredients, self).__AddIngredient(ingredient, description)

  def separate(self, ingredient, out1, out1desc, out2, out2desc, manner):
    return self.__RemoveIngredient(ingredient).__AddIngredient(out1, out1desc).__AddIngredient(out2, out2desc)

  def put(self, ingredient, tool):
    return self.__AddContain(ingredient, tool)

  def remove(self, ingredient, tool):
    return self.__RemoveContain(ingredient, tool)

  def do(self, ingredient, tool, out, outdesc, manner):
    return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc)

  def cut(self, ingredient, tool, out, outdesc, manner):
    return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc)

  def mix(self, ingredient, tool, out, outdesc, manner):
    return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc)

  def cook(self, ingredient, tool, out, outdesc, manner):
    return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc)

  def serve(self, ingredient, manner):
    return self.__RemoveIngredient(ingredient)

  def set(self, tool, setting):
    return self

  def leave(self, ingredient, manner):
    return self

  def chefcheck(self, ingredient, condition):
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
