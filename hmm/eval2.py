from collections import Counter

def to_segmentation_markers(l):
  '''[1, 1, 2, 2, 3, 3, 3, 1] -> [1, 1, 0, 1, 0, 0, 1]'''
  def helper(lst):
    if len(lst) > 0:
      first = lst[0]
      return [0] * (first - 1) + [1] + helper(lst[first:])
    else:
      return []

  return helper(l)[:-1]

def segmentation_scoring(actual, pred):
  assert len(pred) == len(actual)

  counts = Counter(zip(pred, actual))
  true_pos = counts[(1, 1)]
  true_neg = counts[(0, 0)]
  false_pos = counts[(1, 0)]
  false_neg = counts[(0, 1)]

  return float(2 * true_pos) / float(2 * true_pos + false_pos + false_neg)

print to_segmentation_markers([1, 1, 2, 2, 3, 3, 3, 1])
print to_segmentation_markers([2, 2, 2, 2, 2, 2, 2, 2])

def getFScore(actual, pred):
  assert len(pred) == len(actual)

  flat_actual = [x for r in actual for x in to_segmentation_markers(r)]
  flat_pred = [x for r in pred for x in to_segmentation_markers(r)]

  return segmentation_scoring(flat_actual, flat_pred)
