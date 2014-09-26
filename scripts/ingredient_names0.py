from collections import defaultdict
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

def parse_recipe(r):
    units = [
        "cups", "cup",
        "teaspoons", "teaspoon",
        "cans", "can",
        "tablespoons", "tablespoon",
        "packages", "package",
        "pints", "pint",
        "pinches", "pinch",
        "pounds", "pound",
        "bunches", "bunch",
        "bars", "bar",
        "ounces", "ounce",
        "quarts", "quart",
        "dashes", "dash",
        "containers", "container",
        "slices", "slice",
        "envelopes", "envelope",
        "scoops", "scoop",
        "jars", "jar",
        "loaves", "loaf",
        "cubes", "cube",

    ]

    r = reduce(lambda r, u: r.split(" %s " % u, 1)[-1], units, r)
    r = r.split(",", 1)[0]
    r = r.split(") ", 1)[-1]

    return r.strip()

bigrams_cnt = defaultdict(lambda: 0)
def parse_parse(p):
    global bigrams_cnt

    unigrams = []

    stack = p
    while stack:
        i = p.pop(0)

        if len(i) > 1 and isinstance(i[1], list):
            stack += i[1:]
        else:
            unigrams.append(i)
    unigrams = [[None, None]] + unigrams[1:] + [[None, None]]

    

    for a, b in zip(unigrams, unigrams[1:]):
        bigrams_cnt[(a[0], b[1])] += 1

    return p

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
                print parse_sexpr(p)
                print parse_parse(parse_sexpr(p))
                print parse_recipe(t)
                print ""

sorted_bigrams = [p for p in sorted(bigrams_cnt, key=bigrams_cnt.get) if p[0] == "CD"]

total = sum(bigrams_cnt.values())

print [(b, float(bigrams_cnt[b]) / total) for b in sorted_bigrams]
