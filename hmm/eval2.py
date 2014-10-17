from collections import Counter

def to_segmentation_markers(l):
  """Takes output from the HMM decoding algorithm and converts it into a binary
  separator/no separator representation.

  The outputed list will have one less element than the orginal list and will
  contain a 1 at position i if there exists a separator between the i'th and
  i+1'th MILK commands.

  For example, [1, 1, 2, 2, 3, 3, 3, 1] -> [1, 1, 0, 1, 0, 0, 1].

  Args:
    l: a list of numbers, output from the HMM decoder
  Returns:
    A list of list of 0's and 1's designating separators.
  """
  def helper(lst):
    if len(lst) > 0:
      first = lst[0]
      return [0] * (first - 1) + [1] + helper(lst[first:])
    else:
      return []

  return helper(l)[:-1]

def segmentation_scoring(actual, pred):
  """Calculates the F1 score, the harmonic mean of precision and recall.

  Args:
    actual: a list of the true 0's and 1's
    pred: a list of the predicted 0's and 1's
  Returns:
    F1 score
  """
  assert len(pred) == len(actual)

  counts = Counter(zip(pred, actual))
  true_pos = counts[(1, 1)]
  true_neg = counts[(0, 0)]
  false_pos = counts[(1, 0)]
  false_neg = counts[(0, 1)]

  return float(2 * true_pos) / float(2 * true_pos + false_pos + false_neg)

# Some test cases for to_segmentation_markers
# print to_segmentation_markers([1, 1, 2, 2, 3, 3, 3, 1])
# print to_segmentation_markers([2, 2, 2, 2, 2, 2, 2, 2])

def getFScore(actual, pred):
  """Calculates the F1 score for lists of HMM decoded recipes and their true
  segmentations."""
  assert len(pred) == len(actual)

  flat_actual = [x for r in actual for x in to_segmentation_markers(r)]
  flat_pred = [x for r in pred for x in to_segmentation_markers(r)]

  return segmentation_scoring(flat_actual, flat_pred)
