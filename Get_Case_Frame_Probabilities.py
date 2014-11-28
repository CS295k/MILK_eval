from __future__ import division
from sexpdata import loads, ExpectClosingBracket, Symbol
import re
from Data_Interface import getParseCommandPairMappings
from Verb_Alignment_Util import getVerbAlignmentCountDict, getCommandVerbProbability
from MILK_parse import MILK_parse_command
from Case_Frame_Helper import treeToSentence

VERB_TAGS = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

caseFrameCounts = {}
topLevelCounts = {}
exampleSentences = {}

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

def addToCaseframeCounts(caseFrame, vb, command, ingredientsPreviouslyUsed, toolsPreviouslyUsed, sexp, filename):
	givenKey = (vb, ingredientsPreviouslyUsed)
	if givenKey in caseFrameCounts:
		caseFrameDict = caseFrameCounts[givenKey]
		if caseFrame in caseFrameDict:
			caseFrameDict[caseFrame] += 1
			exampleSentences[givenKey][caseFrame].append((filename, parseToSentence(sexp)))
		else:
			caseFrameDict[caseFrame] = 1
			exampleSentences[givenKey][caseFrame] = [(filename, parseToSentence(sexp))]
	else:
		caseFrameCounts[givenKey] = {caseFrame: 1}
		exampleSentences[givenKey] = {caseFrame: [(filename, parseToSentence(sexp))]}

def addToTopLevelCounts(topLevelFrame, numVerbs):
	givenKey = (numVerbs,)
	if givenKey in topLevelCounts:
		topLevelDict = topLevelCounts[givenKey]
		if topLevelFrame in topLevelDict:
			topLevelDict[topLevelFrame] += 1
		else:
			topLevelDict = 1
	else:
		topLevelCounts[givenKey] = {topLevelFrame: 1}

def makeListOfListsHashable(lol):
	'''
	>>> makeListOfListsHashable([[1, 2, 3], [4, 5], -3])
	((1, 2, 3), (4, 5), -3)
	'''
	if type(lol) == list:
		return tuple([makeListOfListsHashable(child) for child in lol])
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

def inputToEnglish(commands, verbs, caseFrameProbabilities, topLevelProbabilities):
	caseFrames = []
	for verb in verbs:
		caseFrame = getMostProbable((verb, False, False), caseFrameProbabilities)
		caseFrame = tuple(["_VP_"] + list(caseFrame)[1:]) # so the case frame isn't replaced again after being added to the top level tree
		caseFrame = replaceOnceInTree(caseFrame, VERB_TAGS, verb)["tree"]
		caseFrames.append(caseFrame)
	topLevel = getMostProbable((len(verbs),), topLevelProbabilities)
	topLevel = ("S1", ("S", ("CCP", "VP", "and", "VP")))
	for caseFrame in caseFrames:
		topLevel = replaceOnceInTree(topLevel, ["VP"], caseFrame)["tree"]
	return treeToSentence(topLevel)

def getMostProbable(given, probs):
	for tup in probs:
		if tup[0][0] == given[0]:
			return tup[1]
	return None

def replaceInTree(tree, tagsToReplace, toReplace):
	if type(tree) == tuple:
		if tree[0] in tagsToReplace:
			newTag = toReplace
		else:
			newTag = tree[0]
		return tuple([newTag] + [replaceInTree(child, tagsToReplace, toReplace) for child in tree[1:]])
	else:
		if tree in tagsToReplace:
			newTag = toReplace
		else:
			newTag = tree
		return newTag

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

parseCommandPairMappings = getParseCommandPairMappings()
for filename in parseCommandPairMappings:
	pairs = parseCommandPairMappings[filename]
	prevPrevIngredients = set()
	prevIngredients = set()
	prevPrevTools = set()
	prevTools = set()
	for pair in pairs:
		command = MILK_parse_command(pair[1])
		if command[0] not in ["create_ing", "create_tool"]:
			try:
				sexp = loads(pair[0])
				vps = getVps(sexp)
				vpVbPair = getMostLikelyVpVbPair(vps, command[0])
				if vpVbPair is not None:
					vp, vb = vpVbPair
					caseFrame = makeListOfListsHashable(getCaseFrame(vp))
					inputIngredients = getInputIngredients(command[0], command[1])
					tools = getTools(command[0], command[1])
					assert(all(re.compile("ing[0-9]+").match(i) for i in inputIngredients))
					assert(all(re.compile("t[0-9]+").match(t) for t in tools))
					ingredientsPreviouslyUsed = len((prevIngredients.union(prevPrevIngredients)).intersection(inputIngredients)) > 0
					toolsPreviouslyUsed = len((prevTools.union(prevPrevTools)).intersection(tools)) > 0
					prevPrevIngredients = prevIngredients
					prevIngredients = getOutputIngredients(command[0], command[1])
					prevPrevTools = prevTools
					prevTools = tools
					if vb is not None and command[0] != "create_ing" and command[0] != "create_tool": # this indicates a bad parse/commands we don't want
						addToCaseframeCounts(caseFrame, vb.lower(), command, ingredientsPreviouslyUsed, toolsPreviouslyUsed, sexp, filename)
						addToTopLevelCounts(makeListOfListsHashable(getTopLevelFrame(sexp)["tree"]), 2)
			except ExpectClosingBracket:
				pass
			except IndexError:
				pass
			except AssertionError:
				print("AssertionError occurred.")

caseFrameProbabilities = []
for key1 in caseFrameCounts:
	denominator = sum(caseFrameCounts[key1][key2] for key2 in caseFrameCounts[key1])
	for key2 in caseFrameCounts[key1]:
		probability = caseFrameCounts[key1][key2] / denominator
		caseFrameProbabilities.append((key1, key2, probability))
caseFrameProbabilities.sort(key=lambda tup: tup[2], reverse=True)

topLevelProbabilities = []
for key1 in topLevelCounts:
	denominator = sum(topLevelCounts[key1][key2] for key2 in topLevelCounts[key1])
	for key2 in topLevelCounts[key1]:
		probability = topLevelCounts[key1][key2] / denominator
		topLevelProbabilities.append((key1, key2, probability))
topLevelProbabilities.sort(key=lambda tup: tup[2], reverse=True)

inputs = [(verbs, caseFrameProbabilities, topLevelProbabilities) for verbs in [["mix", "cook"]]]
for input in inputs:
	print inputToEnglish(None, input[0], input[1], input[2])

# expectedGiven = ("cook", False)
# totalOccurances = sum(caseFrameCounts[expectedGiven][key2] for key2 in caseFrameCounts[expectedGiven])
# print("Conditioning Parameters: " + str(expectedGiven))
# print("Total Occurrences of Key: " + str(totalOccurances))
# print("\n")
# for tup in caseFrameProbabilities:
	# if tup[0] == expectedGiven:
		# print("%s\n%f\n%s\n\n" % (tup[1], tup[2], exampleSentences[tup[0]][tup[1]]))