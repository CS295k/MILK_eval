from __future__ import division
from glob import glob
import re
from MILK_parse import MILK_parse
from Get_Sentence_List import getSentenceList

totalCount = 0
completeNameCount = 0
lastWordOfNameCount = 0
elidedNameCount = 0
otherCount = 0

def cleanString(str):
	str = str.replace("(", "")
	str = str.replace(")", "")
	str = str.replace(",", "")
	str = str.replace("[", "")
	str = str.replace("]", "")
	str = str.replace("+", "and")
	return str

def addToProbabilities(ingredients, sentence, descriptions):
	global totalCount, completeNameCount, lastWordOfNameCount, elidedNameCount, otherCount
	for ing in ingredients:
		name = descriptions[ing]
		sentence = cleanString(sentence)
		name = cleanString(name)
		result = re.search(name, sentence)
		if result is not None:
			completeNameCount += 1
			match = "Complete"
		else:
			nameTokens = name.split()
			result = re.search(nameTokens[-1], sentence)
			if result is not None:
				lastWordOfNameCount += 1
				match = "Last Word"
			else:
				if any(re.search(token, sentence) is not None for token in nameTokens):
					otherCount += 1
					match = "Other"
				else:
					elidedNameCount += 1
					match = "Elided"
		if match == "Elided":
			print(match + ": " + str((name, sentence)))
		totalCount += 1

files = glob("annotated_recipes/*.xml")
for file in [f for f in files if f not in ["annotated_recipes\Bakers-Secret-Pie-Crust.rcp_tagged.xml"]]:
	sentences = getSentenceList(file)
	commands = MILK_parse(file)
	assert(len(commands) == len(sentences))
	
	ingredientDescriptions = {}
	for sentence, command in zip(sentences, commands):
		commandName = command[0]
		commandArgs = command[1]
		if commandName == "create_ing":
			ingredientDescriptions[commandArgs[0]] = commandArgs[1] # set the description for the ingredient
		elif commandName == "combine":
			addToProbabilities(list(commandArgs[0]), sentence, ingredientDescriptions)
			# for arg in commandArgs[0]:
				# del(ingredientDescriptions[arg])
			ingredientDescriptions[commandArgs[1]] = commandArgs[2]
		elif commandName == "separate":
			addToProbabilities([commandArgs[0]], sentence, ingredientDescriptions)
			# del(ingredientDescriptions[commandArgs[0]])
			ingredientDescriptions[commandArgs[1]] = commandArgs[2]
			ingredientDescriptions[commandArgs[3]] = commandArgs[4]
		elif commandName in ["put", "remove"]:
			if type(commandArgs[0]) == type(set()):
				ingredients = list(commandArgs[0])
			else:
				ingredients = [commandArgs[0]]
			addToProbabilities(ingredients, sentence, ingredientDescriptions)
		elif commandName in ["cut", "mix", "cook", "do"]:
			addToProbabilities([commandArgs[0]], sentence, ingredientDescriptions)
			# del(ingredientDescriptions[commandArgs[0]])
			ingredientDescriptions[commandArgs[2]] = commandArgs[3]
		elif commandName == "serve":
			addToProbabilities([commandArgs[0]], sentence, ingredientDescriptions)
			# del(ingredientDescriptions[commandArgs[0]])
		elif commandName in ["leave", "chefcheck"]:
			addToProbabilities([commandArgs[0]], sentence, ingredientDescriptions)

print("============== PROBABILITIES ==============")
print("Complete Name: %f" % (completeNameCount / totalCount))
print("Last Word of Name: %f" % (lastWordOfNameCount / totalCount))
print("Elided Name: %f" % (elidedNameCount / totalCount))
print("Other: %f" % (otherCount / totalCount))
try:
	assert(sum([completeNameCount/totalCount, lastWordOfNameCount/totalCount, elidedNameCount/totalCount, otherCount/totalCount]) == 1)
except:
	print("Sum should add to 1, instead added to: " + str(sum([completeNameCount/totalCount, lastWordOfNameCount/totalCount, elidedNameCount/totalCount, otherCount/totalCount])))