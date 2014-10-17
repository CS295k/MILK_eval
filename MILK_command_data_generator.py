from glob import glob
from MILK_parse import MILK_parse
from Get_Sentence_List import getSentenceList
from itertools import combinations
from nltk.util import ngrams

verbose = 1 #output recipe file names and source command names
simple = 0 #use simple recipe names
#files = glob("annotated_recipes/*.xml")
files = glob("annotated_recipes/1-Pot-3-Bean-Chicken-Stew.rcp_tagged.xml")

ing_dict = {}
simple_ings = {}
possible_names = {}

def permutations(ingredient_desc):
	#l = "orange apple grapes pear"
	s = ingredient_desc.replace(',', '').split()
	res = []
	perms = {}
	for i in range(1,3):
	    res += [' '.join(x) for x in combinations(s,i)] 
	for j in set(res):
		perms[j] = 0
	possible_names[ingredient_desc] = perms
	#print possible_names[ingredient_desc]

#permutations("orange apple grapes pear banana pineapple")


f = open('data/simple_ings2.txt', 'r')
for line in f:
	#print line
	split_line = line.rstrip('\n').split(' -> ')
	#print split_line
	if split_line[1] != 'None':
		simple_ings[split_line[0]] = split_line[1]
		#print simple_ings[split_line[0]]
f.close()

for file in [f for f in files]:

	if file != "annotated_recipes/Bakers-Secret-Pie-Crust.rcp_tagged.xml":
		sentences = getSentenceList(file)
		commands = MILK_parse(file)
		assert(len(commands) == len(sentences))
		if verbose == 1:
			#print(file)
			pass
		ingredientDescriptions = {}
		for sentence, command in zip(sentences, commands):
			commandName = command[0]
			commandArgs = command[1]

			if commandName == "create_ing":
				if simple == 1 and commandArgs[1] in simple_ings:
					ing_dict[commandArgs[0]] = simple_ings[commandArgs[1]]
				else:
					ing_dict[commandArgs[0]] = commandArgs[1]
					permutations(commandArgs[1])
				if verbose == 1:
					#print(commandName + ': ' + commandArgs[0] + ': ' + commandArgs[1])
					pass
				else:
					print(commandArgs[1])
			elif commandName == "create_tool":
				if verbose == 1:
					#print(commandName + ': ' + commandArgs[1])
					pass
				else:
					print(commandArgs[1])
			elif commandName == "combine":
				ing_dict[commandArgs[1]] = commandArgs[2]
				out = ""
				for i in commandArgs[0]:
					out += ing_dict[i] + ', '
				if verbose == 1:
					#print(commandName + ': ' + out + ' -> ' + commandArgs[2] + ', orig text: ' + sentence)
					pass
				else:
					print(commandArgs[2])
			elif commandName == "separate":
				ing_dict[commandArgs[1]] = commandArgs[2]
				ing_dict[commandArgs[3]] = commandArgs[4]
				if verbose == 1:
					#print(commandName + ': ' + ing_dict[commandArgs[0]] + ' ->' + commandArgs[2] + "; " + commandArgs[4])
					pass
				else:
					print(commandArgs[2])
					print(commandArgs[4])
			elif commandName in ["cut", "mix", "cook", "do"]:
				ing_dict[commandArgs[2]] = commandArgs[3]
				if verbose == 1:
					#ing_dict[commandArgs[0]] is the description of the input ingredient
					#we want to see what permutations of the full ingredient name are used
					#in the sentence corresponding to this command
					for n in range(1,3):
						engrams = ngrams(sentence.replace(',', '').replace(';', '').replace('.', '').split(), n)
						for grams in engrams:
							#print ' '.join(grams)
							#print grams
							if ing_dict[commandArgs[0]] in possible_names:
								if ' '.join(grams) in possible_names[ing_dict[commandArgs[0]]]:
									possible_names[ing_dict[commandArgs[0]]][' '.join(grams)] += 1



					#print(ing_dict[commandArgs[0]] + ' -> ' + commandArgs[3] + ', orig text: ' + sentence)
					pass
				else:
					#print(commandArgs[3])
					pass

#print possible_names

for key in possible_names:
	for perm in possible_names[key]:
		if possible_names[key][perm] != 0:
			print key, perm, possible_names[key][perm]

