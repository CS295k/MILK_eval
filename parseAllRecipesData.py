from collections import namedtuple
import re
import cPickle as pickle


Recipe = namedtuple('Recipe', ['title', 'ingredients', 'steps'])

def parseAllRecipes(fn='full_recipes2_cleaned.jsonlines.fixed'):
  with open(fn, 'r') as f:
    normalPattern = re.compile(r"\{\"(?P<name>.*?)\": \[\"(?P<stuff>.*?)\"\]\}")
    emptyPattern = re.compile(r"\{\"(?P<name>.*?)\": \[\]\}")
    def parseRecipe(lines):
      def parseLine(line):
        m = normalPattern.match(line)
        return m.group("name"), m.group("stuff")

      def cleanTitle(title):
        return title.replace('\\n', '') \
          .replace('\\r', '') \
          .replace('\\t', '') \
          .replace(' - Allrecipes.com', '')

      parsedLines = [parseLine(line) for line in lines if not emptyPattern.match(line)]
      title = next((cleanTitle(t) for (n, t) in parsedLines if n == 'title'), None)

      ingredients = [i for (n, i) in parsedLines if n == 'ingredient']
      steps = [s for (n, s) in parsedLines if n == 'step']
      return Recipe(title, ingredients, steps)

    recipes = [parseRecipe([l.strip() for l in r.split('\n') if l.strip() != ''])
             for r in f.read().split('{"end_of_recipe": "END_OF_RECIPE"}')]

    return recipes

  # print recipes[0]
  # print len(recipes)
  # print '\n\n'.join([str(r) for r in recipes if r.title is None])

def saveAllRecipesData(fnin='full_recipes2_cleaned.jsonlines.fixed',
                       fnout='allrecipesdata.pickle'):
  pickle.dump(parseAllRecipes(fnin), open(fnout, 'wb'))

def loadAllRecipesData(fn='allrecipesdata.pickle'):
  return pickle.load(open(fn, 'rb'))
