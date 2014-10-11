from collections import defaultdict
from lxml import etree
from glob import glob


def create_annotated_recipe_generator(n = None):
    i = 0
    for annotated_recipe in glob("../annotated_recipes/*.xml"):
        with open(recipe) as r:
            elt = etree.XML(r.read())
            originaltexts = [line.text for line in elt.findall(".//originaltext")]
            annotations = [line.text for line in elt.findall(".//annotation")]
            yield (originaltexts, annotations)
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
            yield [[parse(p) for p in op[2:-1:2]] for op in originaltext_parses]
            i += 1
            if n and i >= n: break


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


if __name__ == "__main__":
    # WIP