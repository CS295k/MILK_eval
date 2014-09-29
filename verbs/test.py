from nltk import Tree

file = open ("/Users/brawner/workspace/MILK_eval/data/parsed_recipes/1-Pot-3-Bean-Chicken-Stew.txt", "r")

for line in file.readlines():
	if line in ['\n', '\r\n']:
		continue
	values = line.split("\t")
	if len(values) == 2:
		num_parses = int(values[0])
		current_line = int(values[1]) - 1 #parses are 1 indexed
		#print(str(num_parses) + ", " + str(current_line))
	else:
		values = line.split(" ")
		if len(values) == 1:
			log_prob = float(values[0])
			#print(str(log_prob))
		else:
			tree = Tree.fromstring(line)
			print(str(tree))