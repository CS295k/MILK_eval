"""Fits transition and emmission distributions for the HMM model."""

from collections import Counter
from glob import glob
from lxml import etree

def load_recipes():
  """Loads recipes from the data directory. Recipes are represented as
  [(orginaltext, [annotation])]. Returns a list of recipes."""
  recipes = []
  for recipe_file in glob('../annotated_recipes/*.xml'):
    with open(recipe_file, 'r') as recipe_xml:
      recipe_tree = etree.XML(recipe_xml.read())

      original_texts = [x.text for x in recipe_tree.findall('.//originaltext')]
      annotations = [x.text for x in recipe_tree.findall('.//annotation')]

      assert len(original_texts) == len(annotations)

      # Parse recipe, collapsing repeated originaltexts
      recipe = [(original_texts[0], [annotations[0]])]
      for ot, an in zip(original_texts, annotations)[1:]:
        prev_ot, prev_anns = recipe[-1]
        if ot == prev_ot:
          prev_anns.append(an)
        else:
          recipe.append((ot, [an]))

      recipes.append(recipe)

  return recipes

def strip_to_predicate(recipe):
  """Takes a recipe and strips all annotations to their corresponding
  predicates."""
  return [(ot, [x.split('(')[0] for x in anns]) for ot, anns in recipe]

def strip_to_counts(recipe):
  """Takes a recipe and replaces each list of annotations with its length."""
  return [(ot, len(anns)) for ot, anns in recipe]

def remove_create_ing(recipe):
  """Takes a recipe that has been stripped to predicates and removes any lines
  corresponding to only create_ing's."""
  return [(ot, anns) for (ot, anns) in recipe if set(anns) != set(['create_ing'])]

class Dist(dict):
  def __init__(self, numer, denom):
    self.numer = numer
    self.denom = denom

  def __getitem__(self, key):
    return float(self.numer(key)) / float(self.denom(key))

def get_sigma(recipes, zero_index=False):
  """Takes a list of recipes each of which should be stripped to predicates and
  without create_ing's and returns the transition probability matrix sigma."""
  just_counts = [[c for (ot, c) in r] for r in map(strip_to_counts, recipes)]
  transition_counts = Counter([tr for r in just_counts for tr in zip(r, r[1:])])
  marginal_counts = Counter([c for r in just_counts for c in r])

  if zero_index:
    return Dist(lambda (x1, x2): transition_counts[(x1 + 1, x2 + 1)],
                lambda (x1, x2): marginal_counts[x1 + 1])
  else:
    return Dist(lambda (x1, x2): transition_counts[(x1, x2)],
                lambda (x1, x2): marginal_counts[x1])

def get_sigma_independent(recipes):
  """Behaves the same as get_sigma with the exception that states are assumed to
  be independent."""
  just_counts = [[c for (ot, c) in r] for r in map(strip_to_counts, recipes)]
  marginal_counts = Counter([c for r in just_counts for c in r])
  total_lines = sum([len(r) for r in recipes])

  return Dist(lambda x: marginal_counts[x], lambda _: total_lines)

# recipes = map(remove_create_ing, map(strip_to_predicate, load_recipes()))
# for x in [1, 2, 3, 4, 5]: print get_sigma(recipes)[(1, x)]

def get_tau(recipes, zero_index=False):
  """Takes a list of each of which should be stripped to predicates and
  without create_ing's and returns the emmission probability matrix tau."""
  joint = Counter([(len(anns), '_'.join(anns)) for r in recipes for (ot, anns) in r])
  just_counts = [[c for (ot, c) in r] for r in map(strip_to_counts, recipes)]
  marginal_counts = Counter([c for r in just_counts for c in r])

  if zero_index:
    return Dist(lambda (c, anns): joint[(c + 1, anns + 1)],
                lambda (c, anns): marginal_counts[c + 1])
  else:
    return Dist(lambda (c, anns): joint[(c, anns)],
                lambda (c, anns): marginal_counts[c])
