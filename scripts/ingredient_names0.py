from collections import defaultdict, Counter
from lxml import etree
from glob import glob
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


def words_around(sentence, head):
    head = head.lower()
    sentence = regex.sub("", sentence.lower().strip())

    words = sentence.split()
    n = words.index(head) + 1

    return sorted(set([" ".join(p + words[n:n+i]) for p in [words[j:n] for j in range(n)] for i in range(n)]), key = len)[::-1]


if __name__ == "__main__":

    gc = Counter()

    n = 10
    for r, p in zip(create_annotated_recipe_generator(), create_parsed_recipe_generator()):
        limit = count_create_ing(r[2])
        originaltexts = r[1]
        annotations = r[2]
        data = zip([a.split("(", 1)[1].split(",", 1)[0] for a in r[2][:limit]],
                    r[1][:limit], [find_head(p_) for p_ in p[:limit]])
        for datum in data:
            ing = datum[0]
            full = datum[1]
            short = datum[2]

            if not short: continue

            sentences = [o.strip() for o, a in zip(originaltexts, annotations) if ing in a and o != full]
            sentences = [[w.replace(",", "").replace(".", "").lower() for w in s.split()] for s in sentences]
            sentences = sum(sentences, [])
            all_sentences = " ".join(sentences)

            try:
                for phrase in words_around(full, short):
                    if phrase in all_sentences:
                        short = phrase
                        break

                print ("%s -> %s" % (full, short)).encode("utf-8")
            except Exception, e:
                print "ERROR:", e