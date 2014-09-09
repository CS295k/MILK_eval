# CURD Recipe Evaluator

# Written by Frank Goodman (fgoodman)
# 9/9/14

from CURD_parse import CURD_parse

from inspect import stack

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


def CURD_eval(filename):
  commands = CURD_parse(filename)
  return reduce(lambda s, c: s + [(c, getattr(s[-1][1], c[0])(*c[1]))], commands, [(None, WorldState())])
