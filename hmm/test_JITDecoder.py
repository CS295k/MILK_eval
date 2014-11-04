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
from JITDecoder import JITDecoder

if __name__ == "__main__":
  train_paths = glob("./train/*.xml")
  test_paths = glob("./test/*.xml")

  #data_files = glob("../annotated_recipes/*.xml")
  #train_paths, test_paths = train_test_split(data_files, test_size=0.25)

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

  # JIT Decode Test
  n = 4
  best_num = 100
  tagss0 = [[len(anns) for (ot, anns) in r for _ in anns] for r in test_recipes]
  test_cmdss = [[a for (ot, anns) in r for a in anns] for r in test_recipes]

  test_cmds = test_cmdss[0]
  jit_decoder = JITDecoder(n, test_cmds, sigmas_for_decoding, taus_for_decoding, best_num)
  jit_decoder.ping()
  jit_decoder.select(2)
  jit_decoder.ping()
  jit_decoder.select(1)
  jit_decoder.ping()
  jit_decoder.select(3)
  jit_decoder.ping()

  
