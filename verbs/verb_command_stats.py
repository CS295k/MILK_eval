from MILK_eval import MILK_eval, RecipeException
from MILK_parse import MILK_parse_originaltext
from glob import glob
from sys import argv
import os, sys

try:
	from nltk import Tree
except ImportError:
	print("Importing nltk failed. Install it with pip")
	print("sudo pip install -U nltk")
	sys.exit(0)


def read_parse_file(filename, num_parses_to_return = 1):
	sentence_parses = []
	print("Reading file " + filename)
	with open (filename, "r") as myfile:
		num_parses = 0 # Number of parses provided for a sentence, generally 50
		current_line = 0 # Current sentence for whom we're reading parses
		have_parse = False # once the top num_parses_to_return are found, this is set to True
		current_parse = [] # a list of the top parses to return
		was_added = False # Ensure parses aren't added to sentence_parses more than once
		for line in myfile.readlines():

			# An empty line, so the line needs to be to the list of parsed sentences
			if line in ['\n', '\r\n']:
				if not was_added:
					sentence_parses.append(current_parse)
					was_added = True
					have_parse = True
				continue
			
			values = line.split("\t")

			# Encountered new sentence for which to read parses
			if len(values) == 2:
				num_parses = int(values[0])
				current_line = int(values[1]) - 1 #parses are 1 indexed
				have_parse = False
				was_added = False
				continue
				#print(str(num_parses) + ", " + str(current_line))

			# If the parse was read, proceed until the next sentence
			if was_added or have_parse:
				continue

			else:
				values = line.split(" ")
				# Log probability of parse
				if len(values) == 1:
					log_prob = float(values[0])
					#print(str(log_prob))
				# Parse tree on a single line
				else:
					if not have_parse:
						tree = Tree.fromstring(line)
						current_parse.append(tree)
						have_parse = len(current_parse) >= num_parses_to_return
	return sentence_parses

def read_parse_files(parse_files, number_to_read = sys.maxint):
	parses = dict()
	count = 0;
	for parse in parse_files:
		key = os.path.basename(parse).replace(".txt", "")
		parses[key] = read_parse_file(parse)
		if count > number_to_read:
			break
		count += 1
	return parses

def read_milk_commands(recipe_files):
	commands = dict()
	for recipe in recipe_files:
	  try:
	  	milked_commands = MILK_eval(recipe)
	  	milked_sentences = MILK_parse_originaltext(recipe)
	  	key = os.path.basename(recipe).replace(".rcp_tagged.xml", "")
		commands[key] = zip(milked_commands, milked_sentences)
		
	  except RecipeException as e:
	  	pass
	return commands

def condense_commands(commands):
	condensed_commands = dict()
	for recipe, recipe_commands in commands.iteritems():
		condensed_lines = []
		for line in recipe_commands:
			
			predicate = line[0][0]
			params = line[0][1]
			sentence = line[1]

			index = find_sentence_in_list(condensed_lines, line[1])

			if index >= 0:
				condensed_lines[index][0].append(predicate)
				condensed_lines[index][1].append(params)
			else:
				condensed_lines.append(([predicate], [params], sentence))
			
		condensed_commands[recipe] = condensed_lines
	return condensed_commands

def find_sentence_in_list(lines, sentence):
	for i in range(len(lines)):
		if sentence == lines[i][2]:
			return i
	return -1

def get_verbs(parses):
	verb_types = ["VB", "VBP", "VBD", "VBN", "VBG"]
	all_verbs = dict()
	for recipe, recipe_parses in parses.iteritems():
		recipe_verbs = []
		for parse in recipe_parses[0]:
			verbs = []
			for subtree in parse.subtrees(lambda t: t.label() in verb_types):
				label = subtree.label()
				leaf = subtree.leaves()[0]
				verbs.append(leaf)
			recipe_verbs.append(verbs)
		all_verbs[recipe] = recipe_verbs
	return all_verbs

def get_probability(commands, verbs):
	counts = dict()
	for recipe, annotation in commands.iteritems():
		if recipe not in verbs:
			#print("Recipe " + recipe + " not in verbs")
			continue

		recipe_verbs = verbs[recipe]
		if len(annotation) != len(recipe_verbs):
			print("Annotation length not equal for recipe " + recipe)
			print("Length annotation: " + str(len(annotation)) + ", "  + str(len(recipe_verbs)))

		for i in range(len(annotation)):

			predicates = annotation[i][0]
			words = recipe_verbs[i]

			for word in words:
				for predicate in predicates:
					if predicate is None:
						continue
					#print(word)
					if predicate[0] not in counts.keys():
						counts[predicate[0]] = dict()
					if word not in counts[predicate[0]].keys():
						counts[predicate[0]][word] = 0
					counts[predicate[0]][word] += 1

	summed_counts = dict()
	for predicate, word_counts in counts.iteritems():
		for word, count in word_counts.iteritems():
			if predicate not in summed_counts:
				summed_counts[predicate] = 0
			#if count > 0:
			#	print(predicate + ", "  + word  + ", " + str(count))
			summed_counts[predicate] += count

	probabilities = []
	print(str(len(counts)))
	for predicate, word_counts in counts.iteritems():
		for word, count in word_counts.iteritems():
			prob = float(count) / summed_counts[predicate]
			probabilities.append((predicate, word, prob ))

	return sorted(sorted(probabilities, key=lambda probability: probability[2]), key=lambda probability: probability[0])
	



if __name__ == "__main__":
	parse_files = []
	recipe_files = []
	if (len(argv) != 3):
		print("Usage: python get_verb_command_stats.py <recipe_dir> <parses_dir>")
		sys.exit(0)

	recipe_files = glob(argv[1] + "/*.xml")
	parse_files = glob(argv[2] + "/*.txt")
	
	commands = dict()
	if len(parse_files) == 0:
		print("No parse files were found in " + argv[2])
		print(str(parse_files))
		sys.exit(0)
	if len(recipe_files) == 0:
		print("No recipe files were found in " + argv[1])
		print(str(recipe_files))
		sys.exit(0)
	if (len(recipe_files) != len(parse_files)):
		print("The number of recipe files doesn't match the number of recipe files. Weird. " + str(len(recipe_files)) + ", " + str(len(parse_files)))
	
	commands = read_milk_commands(recipe_files)
	condensed_commands = condense_commands(commands)

	parses = read_parse_files(parse_files)
	verbs = get_verbs(parses)
	#print(str(verbs))

	probabilities = get_probability(condensed_commands, verbs)
	for prob in probabilities:
		print(str(prob))
