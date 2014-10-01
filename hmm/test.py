from probs_new import load_recipes
from probs_new import strip_to_predicate
from probs_new import remove_create_ing
from probs_new import get_sigmas
from probs_new import get_taus
from decoder import group_tagging

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

    '''
    cmds = ["combine", "create_tool", "combine", "cook", "combine", \
            "combine", "combine", "create_tool", "create_tool", "cut", \
            "put", "create_tool", "cook"]
    '''



    # Decode
    test_cmds = [["_".join(anns) for (ot, anns) in r] for r in test_recipes]
    n = 4
    alltags = []

    for cmd in test_cmds:
        tags = group_tagging(n, cmd, sigmas_for_decoding, taus_for_decoding)
        tags = [tag+1 for tag in tags]
        alltags.append(tags)

    print alltags
