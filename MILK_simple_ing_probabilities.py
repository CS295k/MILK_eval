from glob import glob
from MILK_parse import MILK_parse
from Get_Sentence_List import getSentenceList

verbose = 1 #output recipe file names and source command names
simple = 1 #use simple recipe names
files = glob("annotated_recipes/*.xml")

ing_dict = {}
simple_ings = {}

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
					#print(commandName + ': ' + out + ' -> ' + commandArgs[2])
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
				if verbose == 1 and commandName == 'cook':
					print(ing_dict[commandArgs[0]] + ' -> ' + commandArgs[3] + ', orig text: ' + sentence)
				else:
					#print(commandArgs[3])
					pass