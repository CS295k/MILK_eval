from probs_new import load_recipes
from probs_new import strip_to_predicate
from probs_new import remove_create_ing, remove_create_tool
from probs_new import get_sigmas
from probs_new import get_taus
from decoder import group_tagging
from EM import forward_algorithm
from EM import backward_algorithm
from eval2 import getFScore
from glob import glob

from sklearn.cross_validation import train_test_split

if __name__ == "__main__":
  #train_paths = glob("./train/*.xml")
  #test_paths = glob("./test/*.xml")

  data_files = glob("../annotated_recipes/*.xml")
  train_paths, test_paths = train_test_split(data_files, test_size=0.25)

  train_recipes = map(remove_create_tool,
                    map(remove_create_ing,
                      map(strip_to_predicate,
                        load_recipes(train_paths))))
  test_recipes = map(remove_create_tool,
                    map(remove_create_ing,
                      map(strip_to_predicate,
                        load_recipes(test_paths))))

  # Train
  sigmas = get_sigmas(train_recipes)
  taus = get_taus(train_recipes)

  sigmas_for_decoding = {}
  taus_for_decoding = {}
  for (s1, s2), sigma in sigmas.iteritems():
    sigmas_for_decoding[(s1-1, s2-1)] = sigma
  for (s, c), tau in taus.iteritems():
    taus_for_decoding[(s-1, c)] = tau

  # Decode
  n = 4
  best_num = 100
  tagss0 = [[len(anns) for (ot, anns) in r for _ in anns] for r in test_recipes]
  best_tagss1 = []
  test_cmdss = [[a for (ot, anns) in r for a in anns] for r in test_recipes]

  # Build up best_tagss1
  for tags0, test_cmds in zip(tagss0, test_cmdss):
    tags1_list = group_tagging(n, test_cmds, sigmas_for_decoding, taus_for_decoding, best_num)
    # From tags1_list, find the best and add to best_tagss1
    best_fscore = 0
    best_tags1 = []
    for tags1 in tags1_list:
      tags1 = [tag+1 for tag in tags1]
      fscore = getFScore([tags0], [tags1])
      if (fscore > best_fscore):
        best_fscore = fscore
        best_tags1 = tags1
    best_tagss1.append(best_tags1)

  '''
  for fn, true, pred in zip(test_paths, tagss0, tagss1):
    print fn
    print "True tags", true
    print "Pred tags", pred
    print


    print 'sigma:'
    for i in range(n):
      print [sigmas_for_decoding.get((i, j), 0) for j in range(n)]
    print
  '''

  fscore = getFScore(tagss0, best_tagss1)
  print "F-Scores"
  print fscore

