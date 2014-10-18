from collections import defaultdict, Counter
from lxml import etree
from glob import glob
from itertools import combinations
from string import punctuation

import re

regex = re.compile('[%s]' % re.escape(punctuation))

def create_annotated_recipe_generator(n = None):
    i = 0
    for annotated_recipe in glob("../annotated_recipes/*.xml"):
        with open(annotated_recipe) as r:
            elt = etree.XML(r.read())
            originaltexts = [line.text for line in elt.findall(".//originaltext")]
            annotations = [line.text for line in elt.findall(".//annotation")]
            yield (annotated_recipe, originaltexts, annotations)
            i += 1
            if n and i >= n: break


def create_parsed_recipe_generator(n = None):
    def parse(sexpr):
        tokens = sexpr.replace("(", " ( ").replace(")", " ) ").split()

        def read_from(tokens):
            if not tokens: raise SyntaxError("Sexpr: Unexpected EOF while reading.")

            token = tokens.pop(0)
            if token == "(":
                L = []
                while tokens[0] != ")":
                    L.append(read_from(tokens))
                tokens.pop(0)
                return L
            elif token == ")":
                raise SyntaxError("Sexpr: Unexpected ')' while reading.")

            return str(token)

        return read_from(tokens)


    def chunks(l, n):
        for i in xrange(0, len(l), n):
            yield l[i:i + n]


    i = 0
    for parsed_recipe in glob("../data/parsed_recipes/*.txt"):
        with open(parsed_recipe) as r:
            originaltext_parses = list(chunks(r.read().splitlines(), 102))
            yield [[parse(p)[1] for p in op[2:-1:2]] for op in originaltext_parses]
            i += 1
            if n and i >= n: break


def count_create_ing(annotations):
    return next((i for i, v in enumerate(annotations) if not v.startswith("create_ing")), -1)


def find_head(parses):
    for p in parses:
        if "NP" in [p_[0] for p_ in p[1:]]:
            break
    else:
        return None

    NPs = [p]
    stack = p[1:]
    while stack:
        node = stack.pop(0)
        if node[0] == "NP":
            NPs.append(node)

        if isinstance(node, list):
            stack = node[1:] + stack

    for NP in NPs[::-1]:
        r = [p[1] for p in NP[1:] if p[0] in {"NN", "NNS", "NNP", "NNPS"}]
        if r:
            return r[-1]
        else:
            return None



stop_words = {"a", "a's", "able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards", "again", "against", "ain't", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything", "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "are", "aren't", "around", "as", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "b", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "both", "brief", "but", "by", "c", "c'mon", "c's", "came", "can", "can't", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "co", "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn't", "course", "currently", "d", "definitely", "described", "despite", "did", "didn't", "different", "do", "does", "doesn't", "doing", "don't", "done", "down", "downwards", "during", "e", "each", "edu", "eg", "eight", "either", "else", "elsewhere", "enough", "entirely", "especially", "et", "etc", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "f", "far", "few", "fifth", "first", "five", "followed", "following", "follows", "for", "former", "formerly", "forth", "four", "from", "further", "furthermore", "g", "get", "gets", "getting", "given", "gives", "go", "goes", "going", "gone", "got", "gotten", "greetings", "h", "had", "hadn't", "happens", "hardly", "has", "hasn't", "have", "haven't", "having", "he", "he's", "hello", "help", "hence", "her", "here", "here's", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him", "himself", "his", "hither", "hopefully", "how", "howbeit", "however", "i", "i'd", "i'll", "i'm", "i've", "ie", "if", "ignored", "immediate", "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates", "inner", "insofar", "instead", "into", "inward", "is", "isn't", "it", "it'd", "it'll", "it's", "its", "itself", "j", "just", "k", "keep", "keeps", "kept", "know", "knows", "known", "l", "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "let's", "like", "liked", "likely", "little", "look", "looking", "looks", "ltd", "m", "mainly", "many", "may", "maybe", "me", "mean", "meanwhile", "merely", "might", "more", "moreover", "most", "mostly", "much", "must", "my", "myself", "n", "name", "namely", "nd", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless", "new", "next", "nine", "no", "nobody", "non", "none", "noone", "nor", "normally", "not", "nothing", "novel", "now", "nowhere", "o", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "on", "once", "one", "ones", "only", "onto", "or", "other", "others", "otherwise", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "own", "p", "particular", "particularly", "per", "perhaps", "placed", "please", "plus", "possible", "presumably", "probably", "provides", "q", "que", "quite", "qv", "r", "rather", "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively", "right", "s", "said", "same", "saw", "say", "saying", "says", "second", "secondly", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "shall", "she", "should", "shouldn't", "since", "six", "so", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "specified", "specify", "specifying", "still", "sub", "such", "sup", "sure", "t", "t's", "take", "taken", "tell", "tends", "th", "than", "thank", "thanks", "thanx", "that", "that's", "thats", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "there's", "thereafter", "thereby", "therefore", "therein", "theres", "thereupon", "these", "they", "they'd", "they'll", "they're", "they've", "think", "third", "this", "thorough", "thoroughly", "those", "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "took", "toward", "towards", "tried", "tries", "truly", "try", "trying", "twice", "two", "u", "un", "under", "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", "used", "useful", "uses", "using", "usually", "uucp", "v", "value", "various", "very", "via", "viz", "vs", "w", "want", "wants", "was", "wasn't", "way", "we", "we'd", "we'll", "we're", "we've", "welcome", "well", "went", "were", "weren't", "what", "what's", "whatever", "when", "whence", "whenever", "where", "where's", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", "whether", "which", "while", "whither", "who", "who's", "whoever", "whole", "whom", "whose", "why", "will", "willing", "wish", "with", "within", "without", "won't", "wonder", "would", "would", "wouldn't", "x", "y", "yes", "yet", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "z", "zero"}
def words_around(sentence, head):
    head = head.lower()
    sentence = regex.sub("", sentence.lower().strip())

    words = sentence.split()
    #print {" ".join(p) for p in permutations(words)}

    words_acc = []
    for w in words:
        try:
            float(w)
        except Exception, e:
            if "/" not in w and w not in stop_words:
                words_acc.append(w)
    words = words_acc

    res = []
    for i in range(1, len(words)):
        res += [' '.join(x) for x in combinations(words, i)] 
    return sorted(res, key = len)
    # return sorted({" ".join(p)permutations(words), key = len)
    # n = words.index(head) + 1

    # return sorted(set([" ".join(p + words[n:n+i]) for p in [words[j:n] for j in range(n)] for i in range(n)]), key = len)


if __name__ == "__main__":
    zp = []
    n = 0
    for r, p in zip(create_annotated_recipe_generator(), create_parsed_recipe_generator()):
        limit = count_create_ing(r[2])
        originaltexts = r[1]
        annotations = r[2]
        data = zip([a.split("(", 1)[1].split(",", 1)[0] for a in r[2][:limit]],
                    r[1][:limit], [find_head(p_) for p_ in p[:limit]])

        originaltext = " ".join(originaltexts[len(data):])

        t = zip(originaltexts[len(data):], annotations[len(data):])

        cnts = defaultdict(Counter)

        for datum in data:
            ing = datum[0]
            full = datum[1]
            head = datum[2]

            # Ignore ingredients without a head
            if not head: continue

            try:
                zpt = defaultdict(set)
                tc = 0
                for phrase in words_around(full, head):
                    cnt = 0
                    for o, a in t:
                        if ing in a:
                            c = o.count(phrase)
                            if c == 0:
                                zpt[(ing, full, head)].add((o, a))
                            cnt += c
                    
                    tc += cnt

                    # # Count the phrase's occurance
                    # cnt = originaltext.count(phrase)
                    cnts[full][phrase] += cnt
                    
                    # Remove double-counts from smaller phrases contained within the larger phrase
                    if cnt:
                        for exist, ecnt in cnts[full].most_common():
                            if ecnt > 0 and phrase != exist and exist in phrase:
                                cnts[full][exist] -= cnt
                if tc == 0:
                    zp.append(zpt)

            except Exception, e:
                # Reached when an improper head is provided to words_around
                pass

        eps = 0.00000001
        for k, v in cnts.items():
            total = sum(v.values())
            top = v.most_common(1)
            if top[0][1] == 0:
                print "%s -> %s (%1.8f)" % (k, top[0][0], eps)
            else:
                print "%s -> %s (%1.1f)" % (k, top[0][0], float(top[0][1]) / total)

    # print zp



            # bestp = None
            # bestc = None
            # for p, c in v.items():
            #     if not bestc or bestc < float(c) / total:
            #         bestp = p
            #         bestc = float(c) / total
            #     #print p, float(c) / total
            # print "%s -> %s %1.1f" % (k, bestp, bestc)
