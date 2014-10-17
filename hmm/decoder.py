# Group Tagger #
# By Qi Xin

import math

def getCmdStr(cmds, i, j):

    # From i (inclusive), take j+1 commands
    # Create the string concatenated by "_"

    len_cmds = len(cmds)
    if (i+j+1 > len_cmds):
        return None
    else:
        return "_".join(cmds[ i : i+j+1 ])
    
# End of Func

def group_tagging(n, cmds, sigmas, taus):

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

    # Matrix Initialization
    # mu: log(len_states x len_cmds)
    mus = [[ 0 for j in xrange(len_states) ] for i in xrange(len_cmds)]
    labels = [[ (-1,-1) for j in xrange(len_states)] for i in xrange(len_cmds)]

    # Build up mus & labels
    for i in xrange(len_cmds):
        for j in xrange(len_states):
            # Get tau
            cmdStr = getCmdStr(cmds, i, j)
            if cmdStr is None:
                #tau_j_i = 0.0
                log_tau_j_i = float('-Inf')
            else:
                # Assume (j, cmdStr) contains
                if (j, cmdStr) not in taus:
                    #tau_j_i = 1e-5
                    log_tau_j_i = math.log(1e-5)
                else:
                    tau_j_i = taus[(j, cmdStr)]
                    if (tau_j_i == 0):
                        log_tau_j_i = math.log(1e-5)
                    else:
                        log_tau_j_i = math.log(tau_j_i)

            if (i == 0):
                #mus[i][j] = 1.0 * tau_j_i
                mus[i][j] = log_tau_j_i
                # The start symbol
                labels[i][j] = (-1,-1)
                
            else:
                # possible moves from the most recent
                #best_mu = 0
                best_mu = float('-Inf')
                best_last = (-1,-1)
                for k in xrange(len_states):
                    last_i = i-k-1

                    # Get last mu & the sigma
                    mu_lasti_k = float('-Inf')
                    sigma_k_j = 0
                    if (last_i < 0):
                        # Can't move by k+1
                        pass
                    else:
                        # States from k to j
                        mu_lasti_k = mus[last_i][k]
                        #sigma_k_j = sigmas[(k, j)]
                        if (k, j) not in sigmas:
                            log_sigma_k_j = math.log(1e-5)
                        else:
                            sigma_k_j = sigmas[(k,j)]
                            if (sigma_k_j == 0):
                                log_sigma_k_j = math.log(1e-5)
                            else:
                                log_sigma_k_j = math.log(sigma_k_j)
                    # End of else

                    #current_mu = mu_lasti_k * sigma_k_j * tau_j_i
                    current_mu = mu_lasti_k + log_sigma_k_j + log_tau_j_i
                    if (current_mu > best_mu):
                        best_mu = current_mu
                        best_last = (last_i, k)
                        
                # End of forloop k
                mus[i][j] = best_mu
                labels[i][j] = best_last
                    
            # End of else
                
        # End of State loop
        
    # End of Cmd loop

    # Trace back
    best_end_mu = float('-Inf')
    best_end_k = -1
    for k in xrange(len_states):
        i = len_cmds - k - 1
        if (i < 0):
            continue
        if (mus[i][k] > best_end_mu):
            best_end_mu = mus[i][k]
            best_end_k = k
    # End of for loop
    best_end_i = len_cmds - best_end_k - 1

    # Create the tags
    tags = []
    last_i = best_end_i
    last_j = best_end_k
    for k in xrange(len_cmds-1, last_i-1, -1):
        tags.insert(0, last_j)
    while (last_i != 0):
        (i, j) = labels[last_i][last_j]
        for k in xrange(last_i-1, i-1, -1):
            tags.insert(0, j)
        last_i = i
        last_j = j
    # End of While loop

    return tags
    
# End of func

if __name__ == "__main__":

    # E.g
    cmds = ["combine", "put", "do"]
    sigmas = {(0,0):0.5, (0,1):0.5, (1,0): 0.5, (1,1): 0.5}
    taus = {(0, "combine"): 0.3, (0, "put"): 0.3, (0, "do"): 0.4, \
            (1, "combine_put"): 0.4, (1, "combine_do"): 0.2, (1, "put_do"): 0.1, \
            (1, "put_combine"): 0.1, (1, "do_combine"): 0.1, (1, "do_put"): 0.1}
    n = 2

    tags = group_tagging(n, cmds, sigmas, taus)
    print(tags)
    

