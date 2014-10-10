from MILK_eval import MILK_eval, RecipeException
from MILK_parse import MILK_parse_originaltext
from glob import glob
from sys import argv
import os, sys, string

try:
  from nltk import Tree
except ImportError:
  print("Importing nltk failed. Install it with pip")
  print("sudo pip install -U nltk")
  sys.exit(0)

TEST_SENTENCE = "Serve with pasta sauce."
MIN_COUNT_REQUIRED = 5

def find_tree_in_list(parses, tree):
  
  for i in range(len(parses)):
    tree_list = parses[i]
    for parse_tree in tree_list:
      if tree == parse_tree:
        return i
  return -1

def get_parse_tree_sentence(tree):
  left_punctuation = [".", ",", "!", ";", ":", "'", "%", ")"]
  right_punctuation = ["("]

  sentence = " ".join(tree.leaves())  
  sentence = sentence.replace("-LRB-", "(")
  sentence = sentence.replace("-LRB- ", "(")
  sentence = sentence.replace(" -RRB-", ")" )
  sentence = sentence.replace("-RRB-", ")" )
  sentence = sentence.replace("& # 34;", '"')
  sentence = sentence.replace("& # 174;", "")
  sentence = sentence.replace("& # 8482;", "")
  for punc in left_punctuation:
    sentence = sentence.replace(" " + punc, punc)
  for punc in right_punctuation:
    sentence = sentence.replace(punc + " ", punc)
  
  return sentence

def clean_sentence(sentence):
  sentence = sentence.strip()
  sentence = " ".join(sentence.split())
  return filter(lambda x: x in string.printable, sentence)
  
def read_parse_file(filename, num_parses_to_return = 1):
  sentence_parses = dict()
  #print("Reading file " + filename)
  with open (filename, "r") as myfile:
    num_parses = 0 # Number of parses provided for a sentence, generally 50
    current_line = 0 # Current sentence for whom we're reading parses
    have_parse = False # once the top num_parses_to_return are found, this is set to True
    for line in myfile.readlines():

      # An empty line, so the line needs to be to the list of parsed sentences
      if line in ['\n', '\r\n']:
        continue
      
      values = line.split("\t")

      # Encountered new sentence for which to read parses
      if len(values) == 2:
        continue
        #print(str(num_parses) + ", " + str(current_line))

      else:
        values = line.split(" ")
        # Log probability of parse
        if len(values) == 1:
          log_prob = float(values[0])
          #print(str(log_prob))
        # Parse tree on a single line
        else:
          tree = Tree.fromstring(line)
          sentence = get_parse_tree_sentence(tree)
          
          if sentence not in sentence_parses.keys():
            sentence_parses[sentence] = tree
            continue
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
      #Skip first because command is null, but not sentence
      milked_commands = milked_commands[1:]
      milked_sentences = MILK_parse_originaltext(recipe)
      key = os.path.basename(recipe).replace(".rcp_tagged.xml", "")
      commands[key] = zip(milked_commands, milked_sentences)
    
    except RecipeException as e:
      pass
  return commands

def condense_commands(commands):
  condensed_commands = dict()
  for recipe, recipe_commands in commands.iteritems():
    condensed_lines = dict()
    for line in recipe_commands:
      
      #Don't want initial state line
      if (line[0][0]) is None:
        continue
      predicate = line[0][0][0]
      params = line[0][0][1]
      sentence = clean_sentence(line[1])
      state = line[0][1]

      if sentence not in condensed_lines.keys():
        condensed_lines[sentence] = []
      condensed_lines[sentence].append((predicate, params, state))

    condensed_commands[recipe] = condensed_lines
  return condensed_commands

def find_sentence_in_list(lines, sentence):
  for i in range(len(lines)):
    if sentence == lines[i][2]:
      return i
  return -1

def get_verbs(parses):
  verb_types = ["VB", "VBP", "VBN"]
  all_verbs = dict()
  for recipe, recipe_parses in parses.iteritems():
    recipe_verbs = dict()
    for sentence, parse in recipe_parses.iteritems():
      verbs = []
      for subtree in parse.subtrees(lambda t: t.label() in verb_types):
        label = subtree.label()
        leaf = subtree.leaves()[0]
        verbs.append(leaf)
      recipe_verbs[sentence] = verbs
    all_verbs[recipe] = recipe_verbs
  return all_verbs

def get_params_to_use(predicate, params, state, dictionary_to_use):
  params_to_use = {
    "combine": [0,1],
    "separate": [0,1,3],
    "put":[0,1],
    "remove":[0,1],
    "cut": [0,1,2],
    "mix": [0,1,2],
    "cook": [0,1,2],
    "do": [0,1,2],
    "serve": [0],
    "set":[1],
    "leave":[0],
    "chefcheck":[0]
  }

  dictionaries = {
    "tool": state.T_d,
    "ingredient": state.I_d,
  }

  indices = []
  if predicate in params_to_use:
    indices = params_to_use[predicate]

  params_to_use = [params[i] for i in indices]



  param_names = []
  
  if dictionary_to_use not in dictionaries.keys():
    print("Dictionary choice must be in " + str(dictionary_to_use.keys()))
    return[]

  d = dictionaries[dictionary_to_use]
  for param in params_to_use:
    if param in d.keys():
      param_names.append(d[param])
  return param_names

def get_probability(commands, verbs, dictionary_to_use):
  counts = dict()
  sentences_not_used = 0
  
  progress = 0
  for recipe, annotation in commands.iteritems():
    progress += 1.0 / len(commands)
    print("Count progress " + str(progress)) 
    

    if recipe not in verbs:
      print("Recipe " + recipe + " not in verbs")
      continue

    recipe_verbs = verbs[recipe]
    #if len(annotation) != len(recipe_verbs):
    #  print("Annotation length not equal for recipe " + recipe)
      #for line in recipe_verbs:
      #  print(str(recipe_verbs))
      #print("Length annotation: " + str(len(annotation)) + ", "  + str(len(recipe_verbs)))
      #for line in annotation:
      #  print(str(line))
    #  continue
    
    for sentence, commands in annotation.iteritems():
      if sentence not in recipe_verbs.keys():
        sentences_not_used += 1
        #print("Skipping '" + sentence + "' because it was not found in " + recipe)
        continue

      words = recipe_verbs[sentence]

      for word in words:
        for command in commands:

          predicate = command[0]
          params = command[1]
          state = command[2]
          print(str(state))
          word = word.lower()

          if predicate not in counts.keys():
            counts[predicate] = dict()

          if word not in counts[predicate].keys():
              counts[predicate][word] = dict()
            
          params = get_params_to_use(predicate, params, state, dictionary_to_use)
          for param in params:
            set_params = []
            if param != None:
              if isinstance(param, basestring):
                set_params.append(param)
              else:
                set_params.extend(param)
            for sparam in set_params:
              if sparam not in counts[predicate][word].keys():
                counts[predicate][word][sparam] = 0
              counts[predicate][word][sparam] += 1

  summed_counts = dict()
  progress = 0
  for predicate, word_counts in counts.iteritems():
    progress += 1.0 / len(counts)
    print("Sum count progress: " + str(progress))
    for word, param_counts in word_counts.iteritems():
      for param, count in param_counts.iteritems():
        if predicate not in summed_counts:
          summed_counts[predicate] = dict()
        if param not in summed_counts[predicate]:
          summed_counts[predicate][param] = 0  
        summed_counts[predicate][param] += count


  probabilities = []
  #print(str(len(counts)))
  progress = 0
  for predicate, word_counts in counts.iteritems():
    progress += 1.0 / len(counts)
    print("Probability count progress: " + str(progress))
    for word, param_counts in word_counts.iteritems():
      for param, count in param_counts.iteritems():
        if summed_counts[predicate][param] > MIN_COUNT_REQUIRED:
          prob = float(count) / summed_counts[predicate][param]
          probabilities.append((predicate, word, param, prob ))
  #print("Could not make use of " + str(sentences_not_used) + " sentences due to poor alignment between corpuses")
  sorted_by_probability = sorted(probabilities, key=lambda probability: probability[3])
  sorted_by_param = sorted(sorted_by_probability, key=lambda probability: probability[2])
  sorted_by_predicate = sorted(sorted_by_param, key=lambda probability: probability[0])


  return sorted_by_predicate
  
def check_sentences(condensed_commands, parses):
  for recipe, condensed_lines in condensed_commands.iteritems():
    if recipe not in parses.keys():
      continue
    parse = parses[recipe]
    if len(parse) != len(condensed_lines):
      print(recipe) 
      print("Command len: " + str(len(condensed_lines)) + " parse len: " + str(len(parse)))

    for command in condensed_lines:
      command_sentence = command[2]
      
      if command_sentence not in parse.keys():
        print(recipe)
        print("\t\'" + command_sentence + "\'")
        for key, value in parse.iteritems():
          print("\t\t\'" + key + "\'")



if __name__ == "__main__":
  parse_files = []
  recipe_files = []
  if (len(argv) != 4):
    print("Usage: python get_verb_command_stats.py <recipe_dir> <parses_dir> <object_type>")
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



  #check_sentences(condensed_commands, parses)
  probabilities = get_probability(condensed_commands, verbs, argv[3])
  for prob in probabilities:
    print(str(prob))
