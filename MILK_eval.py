# MILK Recipe Evaluator

# Written by Frank Goodman (fgoodman)
# 9/9/14

from MILK_parse import MILK_parse

from inspect import stack

class RecipeException(Exception):
  """Raised when an error in the semantic evaluation of a MILK command is encountered."""

  def __init__(self, message):
    caller = str(stack()[2][3])
    if caller == "<lambda>":
      caller = stack()[3][3]

    Exception.__init__(self, "%s: %s" % (caller, message))


class WorldState(object):
  """WorldState is a simplified adaptation of the world state from Tasse's Sour Cream paper.

  Tasse represents a world state as <I, T, S, I_d, T_d, C>. However, because Python's
  dictionaries provide easy access to keys and values, the world state was simplified.
  I is equivalent to I_d's keys, T is equivalent to T_d's keys, and S is equivalent to
  I_d and T_d's values. Thus, CURD_eval represents the world state as <I_d, T_d, C>.

  WorldState is deliberately immutable. Because MILK is based on first-order logic,
  there is a notion of temporal order. Each operation performed on a WorldState creates
  a new WorldState, representing the next state in the order. Storing each state of the
  evaluation allows for easy analysis over the course of the recipe.

  Furthermore, MILK's syntax has been desugared to five operations: 1) add ingredient,
  2) remove ingredient, 3) add tool, 4) add contain, 5) remove contain
  """

  def __init__(self, I_d = {}, T_d = {}, C = set()):
    """Initializes an empty (or pre-populated) world state.

    Arguments:
      I_d (String x String): A mapping of ingredients to descriptions
      T_d (String x String): A mapping of tools to descriptions
      C (String x String): A tuple mapping of tools to ingredients
    """
    self.I_d = I_d
    self.T_d = T_d
    self.C = C


  def __IsNull(self, value):
    """Checks if the provided value is null.

    Arguments:
      value (String): An ingredient, tool, or description

    Returns (Boolean):
      A boolean indicating if the provided value is null
    """
    return value is None or value == "" or value == "null"

  def __IsIngredient(self, ingredient):
    """Checks if the provided ingredient is in the current state.

    Arguments:
      ingredient (String): An ingredient

    Returns (Boolean):
      A boolean indicating if the provided ingredient is in the current state
    """
    return ingredient in self.I_d.keys()

  def __IsTool(self, tool):
    """Checks if the provided tool is in the current state.

    Arguments:
      tool (String): A tool

    Returns (Boolean):
      A boolean indicating if the provided tool is in the current state
    """
    return tool in self.T_d.keys()

  def __IsContain(self, ingredient, tool):
    """Checks if the provided tool contains the provided ingredient in the current state.

    Arguments:
      ingredient (String): An ingredient
      tool (String): A tool

    Returns (Boolean):
      A boolean indicating if the provided tool contains the provided ingredient in the current state
    """
    return (tool, ingredient) in self.C


  def __AddIngredient(self, ingredient, description):
    """Attempt to add an ingredient to the next state.

    Arguments:
      ingredient (String[not-null]): An ingredient
      description (String[not-null]): A description

    Returns (WorldState):
      A new world state containing the provided ingredient and its description
    """
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
    """Attempt to remove an ingredient from the next state.

    Arguments:
      ingredient (String[not-null]): An ingredient

    Returns (WorldState):
      A new world state removing the provided ingredient and its description
    """
    if self.__IsNull(ingredient):
      raise RecipeException("Ingredient must not be null.")

    if not self.__IsIngredient(ingredient):
      raise RecipeException("Ingredient '%s' must already exist." % ingredient)

    I_d = dict(self.I_d)
    del I_d[ingredient]

    return WorldState(I_d, self.T_d, self.C)

  def __RemoveMultipleIngredients(self, ingredients):
    """Attempt to remove multiple ingredients from the next state.

    Arguments:
      ingredients (List[not-null])

    Returns (WorldState):
      A new world state removing the provided ingredients
    """
    if len(ingredients) <= 1:
        raise RecipeException("The number of ingredients must be greater than 1.")
    else:
        ingredientsList = list(ingredients)
        newState = self.__RemoveIngredient(ingredientsList[0])
        for count in xrange(len(ingredientsList)):
            if count > 0:
                newState = newState.__RemoveIngredient(ingredientsList[count])
        return newState

  def __AddTool(self, tool, description):
    """Attempt to add a tool to the next state.

    Arguments:
      tool (String[not-null]): An tool
      description (String[not-null]): A description

    Returns (WorldState):
      A new world state containing the provided tool and its description
    """
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
    """Attempt to add a contain to the next state.

    Arguments:
      ingredient (String[not-null]): An ingredient
      tool (String[not-null]): A tool

    Returns (WorldState):
      A new world state containing the provided contain
    """
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

    C = set(self.C)
    C.add((tool, ingredient))

    return WorldState(self.I_d, self.T_d, C)

  def __RemoveContain(self, ingredient, tool):
    """Attempt to remove a contain from the next state.

    Arguments:
      ingredient (String[not-null]): An ingredient
      tool (String[not-null]): A tool

    Returns (WorldState):
      A new world state containing the provided contain
    """
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

    C = set(self.C)
    if (tool, ingredient) in C: C.remove((tool, ingredient))

    return WorldState(self.I_d, self.T_d, C)

  def __UpdateContain(self, ingredient, out):
    if self.__IsNull(ingredient):
      raise RecipeException("Ingredient must not be null.")

    if self.__IsNull(out):
      raise RecipeException("Ingredient must not be null.")

    if self.__IsIngredient(ingredient):
      raise RecipeException("Ingredient '%s' must not exist." % ingredient)

    if not self.__IsIngredient(out):
      raise RecipeException("Ingredient '%s' must already exist." % out)

    C = set(self.C)
    C = [(k, v) if v != ingredient else (k, out) for (k, v) in C]

    return WorldState(self.I_d, self.T_d, C)

  def create_ing(self, ingredient, description):
    """Creates a new ingredient with the given name and description."""
    return self.__AddIngredient(ingredient, description)

  def create_tool(self, tool, description):
    """Creates a new tool with the given name and description."""
    return self.__AddTool(tool, description)

  def combine(self, ingredients, ingredient, description, manner):
    """Combines the ingredients in the iterable ingredients, creating the new ingredient ingredient."""
    return self.__RemoveMultipleIngredients(ingredients).__AddIngredient(ingredient, description)

  def separate(self, ingredient, out1, out1desc, out2, out2desc, manner):
    """Separates the ingredient ingredient into out1 and out2."""
    return self.__RemoveIngredient(ingredient).__AddIngredient(out1, out1desc).__AddIngredient(out2, out2desc)

  def put(self, ingredient, tool):
    """Places the ingredient into the tool.

    ingredient may be either a single ingredient or a set of ingredients.
    """
    if isinstance(ingredient, set):
      return reduce(lambda s, i: s.__AddContain(i, tool), ingredient, self)
    else:
      return self.__AddContain(ingredient, tool)

  def remove(self, ingredient, tool):
    """Removes the ingredient from the tool."""
    return self.__RemoveContain(ingredient, tool)

  def do(self, ingredient, tool, out, outdesc, manner):
    """Performs a generic action on the ingredient with the provided tool."""
    return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc).__UpdateContain(ingredient, out)

  def cut(self, ingredient, tool, out, outdesc, manner):
    """Cuts the ingredient into pieces with the provided tool."""
    return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc).__UpdateContain(ingredient, out)

  def mix(self, ingredient, tool, out, outdesc, manner):
    """Mixes the ingredient using the provided tool."""
    return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc).__UpdateContain(ingredient, out)

  def cook(self, ingredient, tool, out, outdesc, manner):
    """Cooks or heats the ingredient using the provided tool."""
    if self.__IsNull(tool):
      return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc).__UpdateContain(ingredient, out)
    else:
      return self.__RemoveIngredient(ingredient).__AddIngredient(out, outdesc).__AddContain(out, tool).__UpdateContain(ingredient, out)

  def serve(self, ingredient, manner):
    """Serves the provided ingredient."""
    return self.__RemoveIngredient(ingredient)

  def set(self, tool, setting):
    """Alters the provided tool."""
    return self

  def leave(self, ingredient, manner):
    """Leaves an ingredient alone."""
    return self

  def chefcheck(self, ingredient, condition):
    """Pausing to check if the condition is true."""
    return self


def MILK_eval(filename):
  """Evaluates the MILK file at the given filename.

  Arguments:
    filename (String): A MILK filename

  Returns (List):
    A list of tuples containing the command and its corresponding arguments along with the corresponding WorldState.
  """
  commands = MILK_parse(filename)
  return reduce(lambda s, c: s + [(c, getattr(s[-1][1], c[0])(*c[1]))], commands, [(None, WorldState())])
