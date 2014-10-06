from probs_new import load_recipes
from probs_new import strip_to_predicate
from probs_new import remove_create_ing
from probs_new import get_sigmas
from probs_new import get_taus
from decoder import group_tagging
from collections import Counter


def to_segmentation_markers(lst):
  '''[1, 1, 2, 2, 3, 3, 3, 1] -> [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]'''
  if len(lst) > 0:
    first = lst[0]
    rest = to_segmentation_markers(lst[first:])
    return ([0] * first) if len(rest) == 0 else ([0] * first + [1] + rest)
  else:
    return []

# print to_segmentation_markers([1, 1, 2, 2, 3, 3, 3, 1]) == [0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0]

def segmentation_scoring(pred, actual):
  assert(len(pred) == len(actual))

  counts = Counter(zip(pred, actual))
  true_pos = counts[(1, 1)]
  true_neg = counts[(0, 0)]
  false_pos = counts[(1, 0)]
  false_neg = counts[(0, 1)]

  return float(2 * true_pos) / float(2 * true_pos + false_pos + false_neg)


if __name__ == "__main__":
  train_path = "./train/*.xml"
  test_path = "./test/*.xml"
  train_recipes = map(remove_create_ing, map(strip_to_predicate, load_recipes(train_path)))
  test_recipes = map(remove_create_ing, map(strip_to_predicate, load_recipes(test_path)))

  # Train
  sigmas = get_sigmas(train_recipes)
  taus = get_taus(train_recipes)

  sigmas_for_decoding = {}
  taus_for_decoding = {}
  for (s1, s2), sigma in sigmas.iteritems():
      sigmas_for_decoding[(s1-1, s2-1)] = sigma
  for (s, c), tau in taus.iteritems():
      taus_for_decoding[(s-1, c)] = tau

  '''
  cmds = ["combine", "create_tool", "combine", "cook", "combine", \
          "combine", "combine", "create_tool", "create_tool", "cut", \
          "put", "create_tool", "cook"]
  '''

  # Decode
  # test_recipe_cmds = [["_".join(anns) for (ot, anns) in r] for r in test_recipes]
  test_recipe_cmds = [[a for (ot, anns) in r for a in anns] for r in test_recipes]
  n = 4
  # alltags = []

  actuals = []
  preds = []

  for recipe in test_recipes:
    tags = group_tagging(n, [a for (ot, anns) in recipe for a in anns], sigmas_for_decoding, taus_for_decoding)
    tags = [tag + 1 for tag in tags]

    actual = to_segmentation_markers([len(anns) for (ot, anns) in recipe for _ in anns])
    pred = to_segmentation_markers(tags)

    # Chop to the shortest length
    actual, pred = zip(*zip(actual, pred))

    print actual
    print pred
    print

    actuals.extend(actual)
    preds.extend(pred)

    # alltags.append(tags)

  # print alltags
  print actuals, preds

  print 'F1:', segmentation_scoring(preds, actuals)
