from collections import OrderedDict
from lxml import etree
from glob import glob

def tokenize(s):
    return s.replace("(", " ( ").replace(")", " ) ").split()

def read_from(tokens):
    if not tokens:
        raise SyntaxError("Unexpected EOF while reading.")

    token = tokens.pop(0)
    if token == "(":
        L = []
        while tokens[0] != ")":
            L.append(read_from(tokens))
        tokens.pop(0)
        return L
    elif token == ")":
        raise SyntaxError("Unexpected ) while reading.")
    else:
        return str(token)

def parse_sexpr(s):
    return read_from(tokenize(s))

def parse_parse(p):
    return p[1][1:]

for recipe_file, parse_file in zip(glob("../annotated_recipes/*.xml"), glob("../data/parsed_recipes/*.txt")):
    with open(recipe_file) as rf:
        rfp = etree.XML(rf.read())
        recipe_text = [line.text for line in rfp.findall(".//originaltext")]
        recipe_cmd = [line.text.split("(", 1)[0] for line in rfp.findall(".//annotation")]
        stop = next((i for i, v in enumerate(recipe_cmd) if v != "create_ing"), -1)
        recipe_lines = recipe_text[:stop]
        with open(parse_file) as pf:
            parse_lines = pf.read().splitlines()[4::102]
            
            for t, p in zip(recipe_lines, parse_lines):
                print t
                print parse_parse(parse_sexpr(p))
                print ""
            
