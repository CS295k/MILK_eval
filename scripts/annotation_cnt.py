from collections import Counter
from glob import glob
from lxml import etree

total = Counter()

recipes = 0
lines = 0

for recipe_file in glob('../annotated_recipes/*.xml'):
  with open(recipe_file, 'r') as recipe_xml:
    recipe_tree = etree.XML(recipe_xml.read())

    elements = recipe_tree.findall('.//originaltext')

    lines += len(elements)

    for _, count in Counter([element.text for element in elements]).items():
      total[count] += 1

    recipes += 1


print '\nAnnotations generated (per line of original text):'
for pair in total.items():
  print '%d line(s) of original text generated %d annotations.' % pair

print '\nFor %d total recipes and %d total lines of original text.\n' % (recipes, lines)
