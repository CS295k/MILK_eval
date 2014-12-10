from __future__ import division
from sexpdata import loads, ExpectClosingBracket, Symbol
import re
from Data_Interface import getParseCommandPairMappings
from scripts.MILK_parse import MILK_parse_command
from scripts.Case_Frame_Helper import *

caseFrameCounts = {}
topLevelCounts = {}
exampleSentences = {}

def probabilitiesToFile(probs, filename):
	file = open(filename, "w")
	for tup in probs:
		file.write("%s|%s|%f\n" % (tupleToOutputString(stringsToAscii(tup[0])), treeToString(tup[1]), tup[2]))
	file.close()

def stringsToAscii(tree):
	if type(tree) == tuple:
		return tuple(stringsToAscii(child) for child in tree)
	elif type(tree) == unicode:
		return tree.encode("ascii")
	else:
		return tree

def tupleToOutputString(tup):
	outputList = [str(item) for item in tup]
	return "~".join(outputList)

def treeToString(tree):
	if type(tree) == tuple:
		return "(" + " ".join(treeToString(child) for child in tree) + ")"
	else:
		return tree

def addToCaseframeCounts(caseFrame, vb, command, ingredientsPreviouslyUsed, toolsPreviouslyUsed, sexp, filename):
	givenKey = (vb, ingredientsPreviouslyUsed, toolsPreviouslyUsed)
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
			topLevelDict[topLevelFrame] = 1
	else:
		topLevelCounts[givenKey] = {topLevelFrame: 1}

parseCommandPairMappings = getParseCommandPairMappings()
for filename in parseCommandPairMappings:
	pairs = parseCommandPairMappings[filename]
	prevPrevIngredients = []
	prevIngredients = []
	prevPrevTools = []
	prevTools = []
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
					caseFrame = removeWithPredicate(caseFrame, ["PP"], lambda n: n[1][1] in ["until", "for", "at", "by"])
					caseFrame = removeWithPredicate(caseFrame, ["CC", "ADVP"], lambda n: True)
					inputIngredients = getInputIngredients(command[0], command[1])
					tools = getTools(command[0], command[1])
					assert(all(re.compile("ing[0-9]+").match(i) for i in inputIngredients))
					assert(all(re.compile("t[0-9]+").match(t) for t in tools))
					ingredientsPreviouslyUsed = len((set(prevIngredients).union(set(prevPrevIngredients))).intersection(set(inputIngredients))) > 0
					toolsPreviouslyUsed = len((set(prevTools).union(set(prevPrevTools))).intersection(set(tools))) > 0
					prevPrevIngredients = prevIngredients
					prevIngredients = getOutputIngredients(command[0], command[1])
					prevPrevTools = prevTools
					prevTools = tools
					if vb is not None and command[0] != "create_ing" and command[0] != "create_tool": # this indicates a bad parse/commands we don't want
						addToCaseframeCounts(caseFrame, vb.lower(), command, ingredientsPreviouslyUsed, toolsPreviouslyUsed, sexp, filename)
						topLevel = makeListOfListsHashable(getTopLevelFrame(sexp)["tree"])
						addToTopLevelCounts(topLevel, countVerbs(topLevel))
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

probabilitiesToFile(caseFrameProbabilities, "Case_Frame_Probabilities.txt")
probabilitiesToFile(topLevelProbabilities, "Top_Level_Probabilities.txt")

# expectedGiven = ("cook", False)
# totalOccurances = sum(caseFrameCounts[expectedGiven][key2] for key2 in caseFrameCounts[expectedGiven])
# print("Conditioning Parameters: " + str(expectedGiven))
# print("Total Occurrences of Key: " + str(totalOccurances))
# print("\n")
# for tup in caseFrameProbabilities:
	# if tup[0] == expectedGiven:
		# print("%s\n%f\n%s\n\n" % (tup[1], tup[2], exampleSentences[tup[0]][tup[1]]))