from collections import defaultdict
from lxml import etree
from glob import glob


class Sexpr(object):

    def __init__(self, sexpr):
        self.sexpr = sexpr

    def tokenize(self, sexpr):
        return sexpr.replace("(", " ( ").replace(")", " ) ").split()

    def read_from(self, tokens):
        if not tokens:
            raise SyntaxError("Sexpr: Unexpect EOF while reading.")

        token = tokens.pop(0)
        if token == "(":
            L = []
            while tokens[0] != ")":
                L.append(self.read_from(tokens))
            tokens.pop(0)
            return L
        elif token == ")":
            raise SyntaxError("Sexpr: Unexpect ')' while reading.")
        return str(token)

    def to_list(self):
        return self.read_from(self.tokenize(self.sexpr))


def create_recipe_generator(recipe_file = "../annotated_recipes/*.xml", parse_file = "../data/parsed_recipes/*.txt"):
    def chunks(l, n):
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    for recipe, parse in zip(glob(recipe_file), glob(parse_file)):
        with open(recipe) as r:
            elt = etree.XML(r.read())
            originaltext = [line.text for line in elt.findall(".//originaltext")]
            annotation_cmd = [line.text.split("(", 1)[0] for line in elt.findall(".//annotation")]
            last_create_ing = next((i for i, v in enumerate(annotation_cmd) if v != "create_ing"), -1)
            create_ing = originaltext[:last_create_ing]
            with open(parse) as p:

                originaltext_parses = list(chunks(p.read().splitlines(), 102))

                for originaltext, originaltext_parses in zip(create_ing, originaltext_parses):
                    yield (originaltext, [Sexpr(parse).to_list() for parse in originaltext_parses[2:-1:2]])


class Ingredient(object):

    def __init__(self, sexprs):
        self.sexprs = sexprs

    def simplify(self):

        # sexpr: top ranked parse with a top-level NP
        for sexpr in self.sexprs:
            if "NP" in [s[0] for s in sexpr[1:]]: break
        else:
            return None

        # NPs: all NPs in parse tree found by pre-order DFS
        NPs = [sexpr]
        stack = sexpr[1:]
        while stack:
            node = stack.pop(0)
            if node[0] == "NP":
                NPs.append(node)
            
            if isinstance(node, list):
                stack = node[1:] + stack

        # r: all NN, NNS, NNP, NNPS found
        for NP in NPs[::-1]:
            r = [p[1] for p in NP[1:] if p[0] in {"NN", "NNS", "NNP", "NNPS"}]
            if r:
                return r[-1]
        else:
            return None


if __name__ == "__main__":
    for originaltext, originaltext_parses in create_recipe_generator():
        print "%s -> %s" % (originaltext, Ingredient(originaltext_parses).simplify())
