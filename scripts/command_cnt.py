from collections import defaultdict
from glob import glob
from lxml import etree

total = defaultdict(list)

recipes = 0
lines = 0

for recipe_file in glob('../annotated_recipes/*.xml'):
  with open(recipe_file, 'r') as recipe_xml:
    recipe_tree = etree.XML(recipe_xml.read())

    commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
    originals = [element.text for element in recipe_tree.findall('.//originaltext')]

    for command, original in zip(commands, originals):
      total[command].append(original)
      lines += 1

    recipes += 1

print '\nSentences (per command):'
for command, sentences in total.items():
  print '\'%s\' corresponds with %d sentences (%d unique sentences).' % (command, len(sentences), len(set(sentences)))

print '\nFor %d total recipes and %d total commands.\n' % (recipes, lines)
