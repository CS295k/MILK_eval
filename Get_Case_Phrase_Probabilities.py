from __future__ import division
from sexpdata import loads, ExpectClosingBracket, Symbol
from Data_Interface import getParseCommandPairMappings
from MILK_parse import MILK_parse_command

caseFrameCounts = {}

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

def getVb(verb):
	if type(verb) == list:
		return chooseNonNone([verb[1]._val if verb[0]._val in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"] else None] + [getVb(child) for child in verb[1:]])
	else:
		return None

def addToCaseframeCounts(caseFrame, vb, command):
	givenKey = (vb, command[0])
	if givenKey in caseFrameCounts:
		caseFrameDict = caseFrameCounts[givenKey]
		if caseFrame in caseFrameDict:
			caseFrameDict[caseFrame] += 1
		else:
			caseFrameDict[caseFrame] = 1
	else:
		caseFrameCounts[givenKey] = {caseFrame: 1}

def makeListOfListsHashable(lol):
	'''
	>>> makeListOfListsHashable([[1, 2, 3], [4, 5], -3])
	((1, 2, 3), (4, 5), -3)
	'''
	if type(lol) == list:
		return tuple([makeListOfListsHashable(child) for child in lol])
	else:
		return lol

parseCommandPairMappings = getParseCommandPairMappings()
for filename in parseCommandPairMappings:
	pairs = parseCommandPairMappings[filename]
	for pair in pairs:
		verb = getVerb(pair[0])
		if verb is not None:
			caseFrame = makeListOfListsHashable(getCaseFrame(verb))
			vb = getVb(verb)
			command = MILK_parse_command(pair[1])
			if vb is not None and command[0] != "create_ing" and command[0] != "create_tool": # this indicates a bad parse/commands we don't want
				addToCaseframeCounts(caseFrame, vb.lower(), command) # TODO handle last time NP was mentioned, and extra parameters of command

probabilities = []
for key1 in caseFrameCounts:
	denominator = sum(caseFrameCounts[key1][key2] for key2 in caseFrameCounts[key1])
	for key2 in caseFrameCounts[key1]:
		probability = caseFrameCounts[key1][key2] / denominator
		probabilities.append((key1, key2, probability))

probabilities.sort(key=lambda tup: tup[2])
probabilities.reverse()
for tup in probabilities:
	if tup[0] == ("mix", "mix"):
		print("%s\n%s\n%f\n\n" % tup)