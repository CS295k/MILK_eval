from probs_new import load_recipes
from probs_new import strip_to_predicate
from probs_new import remove_create_ing
from probs_new import get_sigmas
from probs_new import get_taus
from decoder import group_tagging
from EM import forward_algorithm
from EM import backward_algorithm

if __name__ == "__main__":

    train_path = "./train/*.xml"
    test_path = "./test/*.xml"
    train_recipes = map(remove_create_ing, map(strip_to_predicate, load_recipes(train_path)))
    test_recipes = map(remove_create_ing, map(strip_to_predicate, load_recipes(test_path)))

    # Train
    sigmas = get_sigmas(train_recipes)
    taus = get_taus(train_recipes)

    sigmas_for_decoding = {}
    taus_for_decoding = {}
    for (s1, s2), sigma in sigmas.iteritems():
        sigmas_for_decoding[(s1-1, s2-1)] = sigma
    for (s, c), tau in taus.iteritems():
        taus_for_decoding[(s-1, c)] = tau

    # Decode
    n = 4
    tagss0 = [ [len(anns) for (ot, anns) in r for i in xrange(len(anns))] for r in test_recipes]
    tagss1 = []
    test_cmdss = [[a for (ot, anns) in r for a in anns] for r in test_recipes]
    for cmds in test_cmdss:
        tags = group_tagging(n, cmds, sigmas_for_decoding, taus_for_decoding)
        tags = [tag+1 for tag in tags]
        tagss1.append(tags)

    print "True tags"
    print tagss0
    print "Generated tags"
    print tagss1




