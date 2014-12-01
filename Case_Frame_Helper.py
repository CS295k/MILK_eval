from sexpdata import loads, ExpectClosingBracket, Symbol
import re
from Verb_Alignment_Util import getVerbAlignmentCountDict, getCommandVerbProbability

VERB_TAGS = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

def probabilitiesFromFile(filename):
	probs = []
	file = open(filename, "r")
	for line in file:
		tokens = line.split("|")
		given = tupleFromString(tokens[0])
		frame = makeListOfListsHashable(loads(tokens[1]))
		prob = float(tokens[2])
		probs.append((given, frame, prob))
	return probs

def treeToSentence(tree):
	if type(tree) == tuple:
		return " ".join(treeToSentence(child) for child in tree[1:])
	else:
		return tree

def addSentenceCasing(sentence):
	return sentence[0].upper() + sentence[1:]

def addPunctionation(sentence):
	return sentence + "."

def tupleFromString(s):
	tokens = s.split("~")
	tupAsList = []
	for token in tokens:
		if token in ["True", "False"]:
			tupAsList.append(True if token == "True" else False)
		elif isNumeric(token):
			tupAsList.append(float(token))
		else:
			tupAsList.append(token)
	return tuple(tupAsList)

def isNumeric(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def getVerb(parse):
	try:
		if countVerbs(loads(parse)) == 1:
			return retrieveVerb(loads(parse))
		else:
			return None
	except ExpectClosingBracket:
		pass
	except IndexError:
		pass
	except AssertionError:
		pass

def retrieveVerb(sexp):
	if type(sexp) == list:
		return chooseNonNone([sexp if sexp[0]._val == "VP" else None] + [retrieveVerb(child) for child in sexp[1:]])
	else:
		return None

def getVps(sexp):
	if type(sexp) == list:
		verbs = []
		for child in sexp[1:]:
			verbs += getVps(child)
		if sexp[0]._val == "VP":
			verbs.append(sexp)
		return verbs
	else:
		return []

def chooseNonNone(vals):
	# assert(sum([1 for val in vals if val is not None]) <= 1)
	for val in vals:
		if val is not None:
			return val
	return None

def countVerbs(sexp):
	if type(sexp) == list:
		return (1 if sexp[0]._val == "VP" else 0) + sum(countVerbs(child) for child in sexp[1:])
	else:
		return 0

def getCaseFrame(sexp):
	if type(sexp) == list:
		if sexp[0]._val in ["VP", "PP", "IN", "TO", "RP", "PRT"]:
			frameComponents = [sexp[0]._val]
			for child in sexp[1:]:
				frameComponents.append(getCaseFrame(child))
			return frameComponents
		else:
			return sexp[0]._val
	else:
		if type(sexp) == Symbol:
			return sexp._val
		else:
			return sexp

def getTopLevelFrame(sexp):
	if type(sexp) == list:
		newChildren = []
		containsLeaf = False
		for child in sexp[1:]:
			result = getTopLevelFrame(child)
			if result["containsLeaf"]:
				containsLeaf = True
				newChildren.append(result["tree"])
		if containsLeaf:
			return {"containsLeaf": True, "tree": tuple([sexp[0]._val] + newChildren)}
		elif sexp[0]._val in ["VP", "CC"]:
			return {"containsLeaf": True, "tree": sexp[0]._val}
		else:
			return {"containsLeaf": False, "tree": None}
	else:
		return {"containsLeaf": False, "tree": None}

def getVb(verb):
	if type(verb) == list:
		return chooseNonNone([verb[1]._val if verb[0]._val in VERB_TAGS else None] + [getVb(child) for child in verb[1:]])
	else:
		return None

def countTags(sexp, tag):
	if type(sexp) == list:
		return (1 if sexp[0]._val == tag else 0) + sum(countTags(child, tag) for child in sexp[1:])
	else:
		return 0

def parseToSentence(sexp):
	if type(sexp) == list:
		result = ""
		for child in sexp[1:]:
			result += parseToSentence(child)
		return result
	elif type(sexp) == Symbol:
		return str(sexp._val) + " "
	else:
		return str(sexp) + " "

def makeListOfListsHashable(lol):
	'''
	>>> makeListOfListsHashable([[1, 2, 3], [4, 5], -3])
	((1, 2, 3), (4, 5), -3)
	'''
	if type(lol) == list:
		return tuple([makeListOfListsHashable(child) for child in lol])
	elif type(lol) == Symbol:
		return lol._val
	else:
		return lol

def getOutputIngredients(commandName, args):
	if commandName == "create_ing":
		return set([args[0]])
	elif commandName == "combine":
		return set([args[1]])
	elif commandName == "separate":
		return set([args[1], args[3]])
	elif commandName == "put":
		if type(args[0]) in [set, list]:
			return set(args[0])
		else:
			return set([args[0]])
	elif commandName == "remove":
		return set([args[0]])
	elif commandName in ["cut", "mix", "cook", "do"]:
		ingredient = [a for a in args if a is not None and re.compile("ing[0-9]+").match(a)][1]
		return set([ingredient])
	elif commandName in ["serve", "leave", "chefcheck"]:
		return set([args[0]])
	else:
		return set()

def getInputIngredients(commandName, args):
	if commandName == "create_ing":
		return set([args[0]])
	elif commandName == "combine":
		if type(args[0]) in [set, list]:
			return set(args[0])
		else:
			return set([args[0]])
	elif commandName == "separate":
		return set([args[0]])
	elif commandName == "put":
		if type(args[0]) in [set, list]:
			return set(args[0])
		else:
			return set([args[0]])
	elif commandName == "remove":
		return set([args[0]])
	elif commandName in ["cut", "mix", "cook", "do"]:
		return set([args[0]])
	elif commandName in ["serve", "leave", "chefcheck"]:
		return set([args[0]])
	else:
		return set()

def getTools(commandName, args):
	if commandName in ["put", "remove"]:
		# return set([args[1]])
		return set()
	elif commandName in ["cut", "mix", "cook", "do"]:
		tools = [a for a in args if a is not None and re.compile("t[0-9]+").match(a)]
		if len(tools) > 0:
			return set([tools[0]])
		else:
			return set()
	elif commandName == "set":
		return set([args[0]])
	else:
		return set()

def getMostLikelyVpVbPair(initialVps, command):
	counts = getVerbAlignmentCountDict()
	vps = [vp for vp in initialVps if countTags(vp, "VP") == 1 and sum(countTags(vp, vb) for vb in VERB_TAGS) > 0]
	mostLikelyVpVbPair = None
	highestProbability = 0
	for vp in vps:
		vb = getVb(vp).lower()
		prob = getCommandVerbProbability(command, vb, counts)
		if mostLikelyVpVbPair is None or prob > highestProbability:
			mostLikelyVpVbPair = (vp, vb)
			highestProbability = prob
	return mostLikelyVpVbPair

def inputToEnglish(commands, verbs, nouns, caseFrameProbabilities, topLevelProbabilities):
	caseFrames = []
	for verb in verbs:
		caseFrame = getMostProbable((verb, False, False), caseFrameProbabilities)
		caseFrame = ("VP", "VB", "NP", ("PP", ("IN", "in"), "NP"), ("PP", ("IN", "for"), "NP"))
		caseFrame = tuple(["_VP_"] + list(caseFrame)[1:]) # so the case frame isn't replaced again after being added to the top level tree
		caseFrame = replaceOnceInTree(caseFrame, VERB_TAGS, verb)["tree"]
		caseFrame = replaceUnderTag(caseFrame, ["NP"], ["PP"], lambda n: n[1][1]!="for", nouns["tool"], False)
		caseFrame = replaceUnderTag(caseFrame, ["NP"], ["PP"], lambda n: n[1][1]=="for", nouns["manner"], False)
		caseFrame = replaceUnderTag(caseFrame, ["NP"], ["_VP_"], lambda n: True, nouns["ing"], False)
		caseFrames.append(caseFrame)
	topLevel = getMostProbable((len(verbs),), topLevelProbabilities)
	topLevel = ("S1", ("S", ("VP", "VP", ("CC", "and"), "VP")))
	for caseFrame in caseFrames:
		topLevel = replaceOnceInTree(topLevel, ["VP"], caseFrame)["tree"]
	return addPunctionation(addSentenceCasing(treeToSentence(topLevel)))

def getMostProbable(given, probs):
	for tup in probs:
		if tup[0][0] == given[0]:
			return tup[1]
	return None

def replaceOnceInTree(tree, tagsToReplace, toReplace):
	if type(tree) == tuple:
		newChildren = []
		alreadyReplaced = False
		for child in tree[1:]:
			if not alreadyReplaced:
				result = replaceOnceInTree(child, tagsToReplace, toReplace)
				if result["containsReplacement"]:
					alreadyReplaced = True
				newChildren.append(result["tree"])
			else:
				newChildren.append(child)
		if not alreadyReplaced and tree[0] in tagsToReplace:
			newTree = toReplace
		else:
			newTree = tuple([tree[0]] + newChildren)
		return {"containsReplacement": alreadyReplaced, "tree": newTree}
	else:
		if tree in tagsToReplace:
			return {"containsReplacement": True, "tree": toReplace}
		else:
			return {"containsReplacement": False, "tree": tree}

def replaceUnderTag(tree, tagsToReplace, tagsToReplaceUnder, predicate, toReplace, isUnder):
	if type(tree) == tuple:
		if isUnder and tree[0] in tagsToReplace:
			newTree = toReplace
		else:
			newTree = tuple([tree[0]] + [replaceUnderTag(child, tagsToReplace, tagsToReplaceUnder, predicate, toReplace, isUnder or (tree[0] in tagsToReplaceUnder and predicate(tree))) for child in tree[1:]])
		return newTree
	else:
		if isUnder and tree in tagsToReplace:
			return toReplace
		else:
			return tree