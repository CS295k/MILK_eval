# HMM Group Tagger #
# By Qi Xin

from probs_new import *
from EM import *
from JITDecoders import JITDecoder, JITDecoder2

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
        

    def get_JITDecoder2(self, test_recipe_index, n):

        # INPUT:
        # self: the class itself
        # test_recipe_index: the index of the target test recipe
        # n: the number of states

        # RETURN:
        # jit_decoder: just-in-time decoder instance

        test_preds = [a for (ot, anns) in self.test_recipes[test_recipe_index] \
                      for a in anns]
        alphas = forward_algorithm(n, test_preds, self.sigmas, self.taus)
        betas = backward_algorithm(n, test_preds, self.sigmas, self.taus)
        jit_decoder2 = JITDecoder2(n, test_preds, alphas, betas)
        return jit_decoder2

        
    def __init__(self, train_recipes, test_recipes):
        self.train_recipes = train_recipes
        self.test_recipes = test_recipes
        self.sigmas, self.taus = self.train()
