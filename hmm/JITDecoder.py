# HMM Just-in-time Decoder #
# By Qi Xin #

import math
from decoder import *

class JITDecoder:

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
            # Output state_probs
            print "===== State Distribution ====="
            state = 0
            for state_prob in state_probs:
                print (state, state_prob)
                state += 1
            print
        else:
            print "Finish"

    def select(self, state):
        self.index += state + 1

    def __init__(self, n, cmds, sigmas, taus, best_num):
        self.tagss = group_tagging(n, cmds, sigmas, taus, best_num)
        self.n = n
        self.len_cmds = len(cmds)
        self.index = 0
