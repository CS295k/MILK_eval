# Forward & Backward Algorithms #
# EM Algorithm #
# By Qi Xin #

import math
import random

def get_log(val):

    assert val >= 0
    if (val == 0):
        return float("-Inf")
    else:
        return math.log(val)
    

def get_cmd(cmds, i, j):

    # From i (inclusive), take j+1 commands
    # Return the string concatenated by "_"
    # If impossible, return None
    
    len_cmds = len(cmds)
    cmd = None
    if (i+j+1 <= len_cmds):
        cmd = "_".join(cmds[ i : i+j+1 ])
    return cmd
    
def get_tau(taus, i, j, cmds):

    # From i (inclusive), take j+1 commands
    # Create the string concatenated by "_"
    # Then look up the value of tau
    #
    # If impossible, return 0
    # If unseen, return 1e-5

    tau = 0
    cmd = get_cmd(cmds, i, j)
    if not (cmd is None):
        if (j, cmd) not in taus:
            tau = 1e-5
        else:
            tau = taus[(j,cmd)]
    return tau
        
        
def forward_algorithm(n, cmds, sigmas, taus):

   # INPUT:
   # n: the number of states
   # cmds: a list of strings of command
   # sigmas: a dict with key: (state1, state2) & val: prob
   # taus: a dict with key:(state, commandStr) & val: prob
   #
   # NOTE:
   # 1. State begins with 0
   # 2. commandStr is like
   # "combine" for single command or
   # "combine_put_do" for multiple commands
   
   # RETURN:
   # alphas: alpha_y(i)

   len_states = n
   len_cmds = len(cmds)

   # Initialize alphas
   # alphas: len_cmds x len_states
   alphas = [[ 0 for j in xrange(len_states) ] for i in xrange(len_cmds)]

   # Build up alphas
   for i in xrange(len_cmds):
       for j in xrange(len_states):
           tau = get_tau(taus, i, j, cmds)
           # First column
           if (i==0):
               alphas[i][j] = 1.0 * tau
           else:
               for k in xrange(len_states):
                   # Impossible move
                   if (i-k-1 < 0):
                       alphas[i][j] = 0
                   else:
                       ##############
                       '''
                       print k, j
                       print ((k,j) in sigmas)
                       '''
                       ##############
                       sigma = sigmas[(k,j)]
                       alphas[i][j] += alphas[i-k-1][k] * sigma * tau
               # End of iterating k
       # End of iterating j
   # End of iterating i
   
   return alphas
   
# End of Func

def backward_algorithm(n, cmds, sigmas, taus):

    # INPUT:
    # n: the number of states
    # cmds: a list of strings of command
    # sigmas: a dict with key: (state1, state2) & val: prob
    # taus: a dict with key:(state, commandStr) & val: prob
    #
    # NOTE:
    # 1. State begins with 0
    # 2. commandStr is like
    # "combine" for single command or
    # "combine_put_do" for multiple commands

    # RETURN:
    # beta_y(i) = p(x_{i+1,n+1} | y_i)

    len_states = n
    len_cmds = len(cmds)

    # Initialize betas
    # betas: len_cmds x len_states
    betas = [[ 0 for j in xrange(len_states) ] for i in xrange(len_cmds)]

    # Build up betas
    for i in xrange(len_cmds-1, -1, -1):
        for j in xrange(len_states):

            # Impossible move
            if (i+j+1 > len_cmds):
                betas[i][j] = 0
            # Move to the end symbol with certainty
            elif (i+j+1 == len_cmds):
                betas[i][j] = 1
            else:
                # Check every state of (i+j+1)-th column
                for k in xrange(len_states):
                    sigma = sigmas[(j, k)]
                    tau = get_tau(taus, i+j+1, k, cmds)
                    betas[i][j] += sigma * tau * betas[i+j+1][k]
                # End of iterating k

        # End of iterating j
    # End of iterating i
            
    return betas

# End of Func

def get_forward_end_prob(n, cmds, alphas):

    # INPUT:
    # alphas: forward probabilities
    # OUTPUT:
    # alpha_{end}(len_cmds+1)

    alpha_end = 0
    len_cmds = len(cmds)
    for k in xrange(n):
        i = len_cmds - k - 1
        # i<0: impossible move
        if (i >= 0):
            alpha_end += alphas[i][k] * 1.0
    return alpha_end
    

def get_label_prob(i, y_i, alphas, betas, alpha_end):

    # INPUT:
    # i: cmd index
    # y_i: label index
    # alphas: forward probabilities
    # betas: backward probabilities
    # alpha_end: alpha_{end}(len_cmds+1)
    #
    # OUTPUT:
    # p(Y_i=y|x), which is
    # alpha_y(i) x beta_y(i) / alpha_{end}(n+1)

    return alphas[i][y_i] * betas[i][y_i] / alpha_end

def E_Step(n, cmdss, sigmas, taus):

    # INPUT:
    # n: number of states
    # cmdss: all the commands
    # sigmas
    # taus
    # 
    # OUTPUT:
    # (Dict_y_y', Dict_y_x)

    dict1 = {}
    dict2 = {}
    
    for cmds in cmdss:
        
        alphas = forward_algorithm(n, cmds, sigmas, taus)
        betas = backward_algorithm(n, cmds, sigmas, taus)
        alpha_end = get_forward_end_prob(n, cmds, alphas)

        len_cmds = len(cmds)
        for i in xrange(len_cmds):
            for j in xrange(n):
                # Valid move
                if (i+j+1 <= len_cmds):

                    # Compute E[n_{i,y,x}|x]
                    cmd = "_".join(cmds[ i : i+j+1 ])
                    # prob2: p(y_i=j | x)
                    prob2 = alphas[i][j] * betas[i][j] / alpha_end
                    # Update dict2
                    if (j, cmd) not in dict2:
                        dict2[(j, cmd)] = prob2
                    else:
                        dict2[(j, cmd)] += prob2

                    # Compute E[n_{i,y,y'}|x]
                    if (i+j+1 < len_cmds):
                        # y' is not the end symbol
                        for k in xrange(n):
                            # y = j, y' = k
                            # prob1: p(y,y'|x)
                            prob1 = alphas[i][j] * sigmas[(j, k)] * \
                                    get_tau(taus, i+j+1, k, cmds) * betas[i+j+1][k] / \
                                    alpha_end
                            if (j, k) not in dict1:
                                dict1[(j, k)] = prob1
                            else:
                                dict1[(j, k)] += prob1
        
    # End of iterating cmds

    return (dict1, dict2)
                    
def M_Step(n, dict1, dict2):
    
    # INPUT:
    # dict1: Dict_y_y'
    # dict2: Dict_y_x
    #
    # OUTPUT:
    # sigmas, taus

    sigmas = {}
    taus = {}

    dict1o = {}
    dict2o = {}

    # Count sums
    for (s1, s2), c in dict1.iteritems():
        if (s1 not in dict1o):
            dict1o[s1] = c
        else:
            dict1o[s1] += c

    for (s, cmd), c in dict2.iteritems():
        if (s not in dict2o):
            dict2o[s] = c
        else:
            dict2o[s] += c

    # Build up sigmas & taus
    for (s1, s2), c in dict1.iteritems():
        sigmas[(s1, s2)] = float(c) / float(dict1o[s1])

    for (s, cmd), c in dict2.iteritems():
        taus[(s, cmd)] = float(c) / float(dict2o[s])

    return (sigmas, taus)

def init_sigmas(n, init_val):

    # INPUT:
    # n: number of states
    # init_val: default value
    # 
    # OUTPUT:
    # initialized sigmas with random probs

    sigmas = {}
    for i in xrange(n):
        for j in xrange(n):
            # In case of saddle point
            r = random.random() * 0.1 + 0.95
            sigmas[(i,j)] = r * init_val
    return sigmas

def init_taus(n, cmdss, init_val):
    
    # INPUT:
    # n: number of states
    # cmdss: all the commands
    # init_val: default value
    #
    # OUTPUT:
    # initialized taus with random probs

    taus = {}
    for cmds in cmdss:
        len_cmds = len(cmds)
        for i in xrange(len_cmds):
            for j in xrange(n):
                cmd = get_cmd(cmds, i, j)
                # Possible move
                if not (cmd is None):
                    if (j, cmd) not in taus:
                        # In case of saddle point
                        r = random.random() * 0.1 + 0.95
                        taus[(j, cmd)] = r * init_val
    return taus

def EM(n, cmdss):

    # INPUT:
    # n: number of states
    # cmdss: all the commands

    # OUTPUT:
    # sigmas, taus

    sigmas = init_sigmas(n, 0.1)
    taus = init_taus(n, cmdss, 0.1)
    for iter in xrange(40):
        ###########
        print iter
        ###########
        dict1, dict2 = E_Step(n, cmdss, sigmas, taus)
        sigmas, taus = M_Step(n, dict1, dict2)
    return (sigmas, taus)


    
