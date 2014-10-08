def segmentation_scoring(pred, actual):
  assert(len(pred) == len(actual))

  counts = Counter(zip(pred, actual))
  true_pos = counts[(1, 1)]
  true_neg = counts[(0, 0)]
  false_pos = counts[(1, 0)]
  false_neg = counts[(0, 1)]

  return float(2 * true_pos) / float(2 * true_pos + false_pos + false_neg)
