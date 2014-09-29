from __future__ import division
from glob import glob
import re
from MILK_parse import MILK_parse
from Get_Sentence_List import getSentenceList

totalCount = 0
completeNameCount = 0
lastWordOfNameCount = 0
onlyLastWordOfNameCount = 0
elidedNameCount = 0
mightBePronounCount = 0
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
	global totalCount, completeNameCount, lastWordOfNameCount, onlyLastWordOfNameCount, elidedNameCount, mightBePronounCount, otherCount
	for ing in ingredients:
		name = descriptions[ing]
		cleanedSentence = cleanString(sentence)
		cleanedName = cleanString(name)
		if re.search(cleanedName, cleanedSentence) is not None:
			completeNameCount += 1
			match = "Complete"
		else:
			nameTokens = cleanedName.split()
			if re.search(nameTokens[-1], cleanedSentence) is not None:
				if len(nameTokens) >= 2 and re.search(nameTokens[-2] + " " + nameTokens[-1], cleanedSentence) is not None:
					lastWordOfNameCount += 1
					match = "Last Word"
				else:
					onlyLastWordOfNameCount += 1
					match = "Only Last Word"
			else:
				if any(re.search("\\b"+pronoun+"\\b", cleanedSentence) is not None for pronoun in ["it", "they", "them"]):
					mightBePronounCount += 1
					match = "Pronoun"
				else:
					if any(re.search(token, cleanedSentence) is not None for token in nameTokens):
						otherCount += 1
						match = "Other"
					else:
						elidedNameCount += 1
						match = "Elided"
		if match == "Last Word":
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
			if type(commandArgs[0]) in [type(set()), type([])]:
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
print("Only Last Word of Name: %f" % (onlyLastWordOfNameCount / totalCount))
print("Last Word of Name: %f" % (lastWordOfNameCount / totalCount))
print("Elided Name: %f" % (elidedNameCount / totalCount))
print("Potential Pronoun: %f" % (mightBePronounCount / totalCount))
print("Other: %f" % (otherCount / totalCount))
summ = sum([completeNameCount/totalCount, lastWordOfNameCount/totalCount, onlyLastWordOfNameCount/totalCount, elidedNameCount/totalCount, mightBePronounCount/totalCount, otherCount/totalCount])
try:
	assert(summ == 1)
except:
	print("Sum should add to 1, instead added to: " + str(summ))