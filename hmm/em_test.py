from probs_new import load_recipes
from probs_new import strip_to_predicate
from probs_new import remove_create_ing, remove_create_tool
from probs_new import get_sigmas
from probs_new import get_taus
from decoder import group_tagging
from EM import *
from eval2 import getFScore
from glob import glob

if __name__ == "__main__":

    train_path = "./train/*.xml"
    test_path = "./test/*.xml"
    train_recipes = map(remove_create_tool,
                        map(remove_create_ing,
                            map(strip_to_predicate,
                                load_recipes(train_path))))
    test_recipes = map(remove_create_tool,
                       map(remove_create_ing,
                           map(strip_to_predicate,
                               load_recipes(test_path))))
    
    train_cmdss = [[a for (ot, anns) in r for a in anns] for r in train_recipes]
    test_cmdss = [[a for (ot, anns) in r for a in anns] for r in test_recipes]

    # Unsupervised Learning
    n = 4
    sigmas_for_decoding, taus_for_decoding = EM(4, train_cmdss)

    ##################
    #print sigmas, taus
    ##################

    # Decode
    tagss0 = [[len(anns) for (ot, anns) in r for _ in anns] for r in test_recipes]
    tagss1 = []
    for cmds in test_cmdss:
        tags = group_tagging(n, cmds, sigmas_for_decoding, taus_for_decoding)
        tags = [tag+1 for tag in tags]
        tagss1.append(tags)

    # Eval
    fscore = getFScore(tagss0, tagss1)
    print "F-Scores"
    print fscore
          
