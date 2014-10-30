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

def getSigma(state1, state2, sigmas):

    # Smooth
    if (state1, state2) not in sigmas:
        sigma = 1e-5
    else:
        sigma = sigmas[(state1,state2)]
        if (sigma == 0):
            sigma = 1e-5
    return sigma
            
def getTau(i, j, cmdStr, taus):

    # Smooth
    if cmdStr is None:
        tau = 0
    elif (j, cmdStr) not in taus:
        tau = 1e-5
    else:
        tau = taus[(j, cmdStr)]
        if (tau == 0):
            tau = 1e-5
    return tau

def group_tagging(n, cmds, sigmas, taus, best_num):

    # INPUT:
    # n: the number of states
    # cmds: a list of strings of command
    # sigmas: a dict with key: (state1, state2) & val: prob
    # taus: a dict with key:(state, commandStr) & val: prob
    # best_num: find best sequences in number of best_num
    #
    # NOTE:
    # 1. State begins with 0
    # 2. commandStr is like
    # "combine" for single command or
    # "combine_put_do" for multiple commands

    # RETURN:
    # tagss: best_num lists of grouping labels

    len_states = n
    len_cmds = len(cmds)

    # Matrix Initialization
    # size of log_mus & labels: len_states x len_cmds x k
    log_mus = [[ [float('-Inf') for k in xrange(best_num)] for j in xrange(len_states) ] for i in xrange(len_cmds)]
    labels = [[ [(-2,-2,-2) for k in xrange(best_num)] for j in xrange(len_states)] for i in xrange(len_cmds)]

    # Build up log_mus & labels
    for i in xrange(len_cmds):
        for j in xrange(len_states):
            # Get tau
            cmdStr = getCmdStr(cmds, i, j)
            tau = getTau(i, j, cmdStr, taus)
            if (tau == 0):
                log_tau = float('-Inf')
            else:
                log_tau = math.log(tau)

            if (i == 0):
                #mus[0][j][0] = 1.0 * tau
                log_mus[i][j][0] = log_tau
                #label[0][j][0] is the start symbol
                labels[i][j][0] = (-1,-1,-1)
                
            else:
                last_best_num_index_list = [ 0 for k in xrange(len_states) ]
                for best_iter in xrange(best_num):
                    # Possible moves from the last state k,
                    # Find the largest to fill mus/labels[i][j][best_iter]
                    best_log_mu = float('-Inf')
                    best_label = (-2,-2,-2)
                    for k in xrange(len_states):
                        last_i = i-k-1
                        if (last_i >= 0):
                            # Valid move from state k to j
                            last_best_num_index = last_best_num_index_list[k]
                            last_log_mu = log_mus[last_i][k][last_best_num_index]
                            sigma = getSigma(k, j, sigmas)
                            log_sigma = math.log(sigma)
                            current_log_mu = last_log_mu + log_sigma + log_tau
                            if (current_log_mu > best_log_mu):
                                best_log_mu = current_log_mu
                                best_label = (last_i, k, last_best_num_index)
                             
                    # End of forloop k
                    best_k = best_label[1]
                    if (best_k != -2):
                        last_best_num_index_list[best_k] += 1
                    log_mus[i][j][best_iter] = best_log_mu
                    labels[i][j][best_iter] = best_label

    # Build up end_log_mus & end_labels
    # end_log_mus[0:best_num] <=> log_mus[len_cmds+1][<|][0:best_num]
    # end_labels[0:best_num] <=> labels[len_cmds+1][<|][0:best_num]

    #########################
    #print "End up building log_mus & labels"
    #########################
    
    end_log_mus = [ float('-Inf') for k in xrange(best_num) ]
    end_labels = [ (-2,-2,-2) for k in xrange(best_num) ]
    last_best_num_index_list = [ 0 for k in xrange(len_states) ]
    for best_iter in xrange(best_num):
        best_log_mu = float('-Inf')
        best_label = (-2,-2,-2)
        for k in xrange(len_states):
            last_i = len_cmds-k-1
            if (last_i >= 0):
                # Valid move from state k to <|
                last_best_num_index = last_best_num_index_list[k]
                last_log_mu = log_mus[last_i][k][last_best_num_index]
                current_log_mu = last_log_mu
                if (current_log_mu > best_log_mu):
                    best_log_mu = current_log_mu
                    best_label = (last_i, k, last_best_num_index)
        # End of forloop k
        best_k = best_label[1]
        if (best_k != -2):
            last_best_num_index_list[best_k] += 1
        end_log_mus[best_iter] = best_log_mu
        end_labels[best_iter] = best_label


    #########################
    #print "End up building end_mus & end_labels"
    #########################

    # Create the tagss
    # Note: the size of tagss could be LESS than best_num
    tagss = []
    for best_iter in xrange(best_num):
        tags = []
        if (end_log_mus[best_iter] == float('-Inf')):
            break
        (last_i, last_j, last_index) = end_labels[best_iter]
        # From len_cmds-1 back to last_i, label as last_j
        for k in xrange(len_cmds-1, last_i-1, -1):
            tags.insert(0, last_j)
        while (last_i != 0):
            (i, j, index) = labels[last_i][last_j][last_index]
            for k in xrange(last_i-1, i-1, -1):
                tags.insert(0, j)
            last_i, last_j, last_index = i, j, index
        tagss.append(tags)

    return tagss
    
# End of func

if __name__ == "__main__":

    # E.g
    cmds = ["combine", "put", "do"]
    sigmas = {(0,0):0.5, (0,1):0.5, (1,0): 0.5, (1,1): 0.5}
    taus = {(0, "combine"): 0.3, (0, "put"): 0.3, (0, "do"): 0.4, \
            (1, "combine_put"): 0.4, (1, "combine_do"): 0.2, (1, "put_do"): 0.1, \
            (1, "put_combine"): 0.1, (1, "do_combine"): 0.1, (1, "do_put"): 0.1}
    n = 2
    best_num = 3

    tagss = group_tagging(n, cmds, sigmas, taus, best_num)
    print(tagss)
    

