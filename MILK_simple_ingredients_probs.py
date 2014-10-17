from glob import glob
from MILK_parse import MILK_parse
from Get_Sentence_List import getSentenceList
from itertools import combinations
from nltk.util import ngrams

verbose = 1 #output recipe file names and source command names
simple = 0 #use simple recipe names
files = glob("annotated_recipes/*.xml")
#files = glob("annotated_recipes/Absolutely-Awesome-BBQ-Sauce.rcp_tagged.xml")

ing_dict = {}
simple_ings = {}
possible_names = {}

stoplist = ['1', '2', 'in', 'the', 'a', 'an', 'and', 'or', '1/2', '1/3', '1/4', 'into', 'inch', 'cup']

def permutations(ingredient_desc):
	#l = "orange apple grapes pear"
	s = ingredient_desc.replace(',', '').split()
	res = []
	perms = {}
	for i in range(1,4):
	    res += [' '.join(x) for x in combinations(s,i)] 
	for j in set(res):
		perms[j] = 0
	possible_names[ingredient_desc] = perms
	#print possible_names[ingredient_desc]

def ngram_counter(x, ingredient_desc, sentence, increment):
	if x == 0:
		return;
	#print 'kapow'
	for n in range(1, x):
		engrams = ngrams(sentence.replace(',', '').replace(';', '').replace('.', '').split(), n)
		for grams in engrams:
			#if ingredient_desc == '1 bay leaf':
				#print ' '.join(grams)
			#print grams
			if ingredient_desc in possible_names:
				if ' '.join(grams) in possible_names[ingredient_desc] and ' '.join(grams) not in stoplist and grams[-1] not in stoplist:
					possible_names[ingredient_desc][' '.join(grams)] += increment
					for c in  ngrams(' '.join(grams).split(), n-1):
						#print ' '.join(c), ' '.join(grams)
						if ' '.join(c) != ' '.join(grams):
							#print ' '.join(c)
							possible_names[ingredient_desc][' '.join(c)] = 0 
							pass
					
					#ngram_counter(n-1, ' '.join(grams), sentence, -1)


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
					#print(ing_dict[commandArgs[0]] + ' -> ' + commandArgs[3] + ', orig text: ' + sentence)
					pass
				else:
					#print(commandArgs[3])
					pass

			#start of probability calculations
			if commandName in ["combine"]:
				for i in commandArgs[0]:
					ngram_counter(4, ing_dict[i], sentence, 1.0)
					'''
					for n in range(1,4):
						engrams = ngrams(sentence.replace(',', '').replace(';', '').replace('.', '').split(), n)
						for grams in engrams:
							#print ' '.join(grams)
							#print grams
							if ing_dict[i] in possible_names:
								if ' '.join(grams) in possible_names[ing_dict[i]]:
									possible_names[ing_dict[i]][' '.join(grams)] += 1	
					'''
			if commandName in ["cut", "mix", "cook", "do", "separate"]:
				#ing_dict[commandArgs[0]] is the description of the input ingredient
				#we want to see what permutations of the full ingredient name are used
				#in the sentence corresponding to this command
				ngram_counter(4, ing_dict[commandArgs[0]], sentence, 1.0)
				'''
				for n in range(1,4):
						engrams = ngrams(sentence.replace(',', '').replace(';', '').replace('.', '').split(), n)
						for grams in engrams:
							#print ' '.join(grams)
							#print grams
							if ing_dict[commandArgs[0]] in possible_names:
								if ' '.join(grams) in possible_names[ing_dict[commandArgs[0]]]:
									possible_names[ing_dict[commandArgs[0]]][' '.join(grams)] += 1
				'''

#print possible_names

for key in possible_names:
	count = 0.0
	for perm in possible_names[key]:
		if possible_names[key][perm] != 0:
			count += possible_names[key][perm]
	if count != 0:
		for perm in possible_names[key]:
			if possible_names[key][perm] != 0:
				print (key + ' -> ' + perm + ': ' + str(possible_names[key][perm]/count)).encode("utf-8")

