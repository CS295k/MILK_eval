from __future__ import division
from glob import glob
from os.path import basename

def getVerbAlignmentCountDict():
	counts = {}
	recipeNumber = 0
	for filename in glob("verbAlignments/*"):
		if basename(filename) != "README":
			if recipeNumber % 10 != 0: # if this recipe is in the training set
				addToVerbAlignmentCounts(filename, counts)
			recipeNumber += 1
	return counts

def addToVerbAlignmentCounts(filename, counts):
	file = open(filename, "r")
	for line in file:
		tokens = line.split()
		i = 0
		while i < len(tokens):
			command = tokens[i]
			verb = tokens[i+1].lower()
			if verb != "noverb":
				addToDict(command, verb, counts)
			i += 2

def addToDict(command, verb, counts):
	if command in counts:
		if verb in counts[command]:
			counts[command][verb] += 1
		else:
			counts[command][verb] = 1
	else:
		counts[command] = {verb: 1}

def getCommandVerbProbability(command, verb, counts):
	return getBigramCount(command, verb, counts) / getUnigramCount(command, counts)

def getBigramCount(command, verb, counts):
	if command in counts:
		if verb in counts[command]:
			return counts[command][verb]
		else:
			return 0
	else:
		return 0

def getUnigramCount(command, counts):
	if command in counts:
		return sum(getBigramCount(command, verb, counts) for verb in counts[command])
	else:
		return 0

# counts = getVerbAlignmentCountDict()
# command = "cook"
# probs = []
# for verb in counts[command]:
	# probs.append((verb, getCommandVerbProbability(command, verb, counts)))
# probs.sort(key=lambda pair: pair[1], reverse=True)
# for prob in probs:
	# print prob