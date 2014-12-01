# HMM Just-in-time Decoders #
# By Qi Xin #

import math
from decoder import *

class JITDecoder:

    ###################################################
    # Compute Group frequencies from k best sequences #
    ###################################################
    
    def ping(self):
        if (self.index < self.len_cmds):
            state_counts = [ 0 for i in xrange(self.n) ]
            for tags in self.tagss:
                state = tags[self.index]
                state_counts[state] += 1
            sum_counts = 0
            for state_count in state_counts:
                sum_counts += state_count
            state_probs = [ float(state_count)/float(sum_counts) \
                            for state_count in state_counts ]
            return state_probs
        else:
            return None

    def select(self, state):
        self.index += state + 1

    def __init__(self, n, cmds, sigmas, taus, best_num):
        self.tagss = group_tagging(n, cmds, sigmas, taus, best_num)
        self.n = n
        self.len_cmds = len(cmds)
        self.index = 0


class JITDecoder2:

    ###################
    # Compute p(Yi|x) #
    ###################
    
    def ping(self):
        index = self.index
        n = self.n
        if (index < self.len_cmds):
            state_probs = [ self.alphas[index][j] * self.betas[index][j] \
                            for j in xrange(n) ]
            norm = sum(state_probs)
            state_probs = [ prob/norm for prob in state_probs ]
            return state_probs
        else:
            return None
            
    def select(self, state):
        self.index += state + 1

    def __init__(self, n, cmds, alphas, betas):
        self.n = n
        self.len_cmds = len(cmds)
        self.index = 0
        self.alphas = alphas
        self.betas = betas
