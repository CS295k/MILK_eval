# HMM Group Tagger #
# By Qi Xin

from probs_new import *
from JITDecoder import JITDecoder

def strip(paths):
        
    recipes = map(remove_create_tool,
                  map(remove_create_ing,
                      map(strip_to_predicate,
                          load_recipes(paths))))
    return recipes


class group_tagger:

    def train(self):

        sigmas_tmp = get_sigmas(self.train_recipes)
        taus_tmp = get_taus(self.train_recipes)
        sigmas = {}
        taus = {}
        for (s1, s2), sigma in sigmas_tmp.iteritems():
            sigmas[(s1-1, s2-1)] = sigma
        for (s, c), tau in taus_tmp.iteritems():
            taus[(s-1, c)] = tau
        return (sigmas, taus)

    def get_JITDecoder(self, test_recipe_index, n, best_num):

        # INPUT:
        # self: the class itself
        # test_recipe_index: the index of the target test recipe
        # n: the number of states
        # best_num: best_num sequences will be considered

        # RETURN:
        # jit_decoder: just-in-time decoder instance
        
        test_preds = [a for (ot, anns) in self.test_recipes[test_recipe_index] \
                      for a in anns]
        jit_decoder = JITDecoder(n, test_preds, self.sigmas, self.taus, best_num)
        return jit_decoder
        
        
    def __init__(self, train_paths, test_paths):
        self.train_recipes = strip(train_paths)
        self.test_recipes = strip(test_paths)
        self.sigmas, self.taus = self.train()
