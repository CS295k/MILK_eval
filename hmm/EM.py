# Forward & Backward Algorithms #
# EM Algorithm #
# By Qi Xin

import math

def get_log(val):

    assert val >= 0
    if (val == 0):
        return float("-Inf")
    else:
        return math.log(val)
    

def get_tau(taus, i, j, cmds):

    # From i (inclusive), take j+1 commands
    # Create the string concatenated by "_"
    # Then look up the value of tau

    tau = 0
    len_cmds = len(cmds)
    if (i+j+1 <= len_cmds):
        cmd = "_".join(cmds[ i : i+j+1 ])
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
   # tags: a list of grouping labels

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
