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

def get_stripped_sentence_commands(sentence_commands, predicates_to_ignore):
  stripped_commands = []
  for command in sentence_commands:
    if command[0] not in predicates_to_ignore:
      stripped_commands.append(command)
  return stripped_commands

def get_commands_of_length(commands, length = 1, predicates_to_ignore=["create_ing", "create_tool"]):
  commands_of_length = dict()
  for recipe, recipe_commands in commands.iteritems():
    recipe_commands_of_length = dict()
    for sentence, sentence_commands in recipe_commands.iteritems():
      sentence_commands_of_length = []
      stripped_commands = get_stripped_sentence_commands(sentence_commands, predicates_to_ignore)
      if len(stripped_commands) == length:
        recipe_commands_of_length[sentence] = stripped_commands
    commands_of_length[recipe] = recipe_commands_of_length
  return commands_of_length

def get_parses_of_length(parses, length = 1, nonterminals=["VP"]):
  parses_of_length = dict()
  for recipe, recipe_parses in parses.iteritems():
    recipe_parses_of_length = dict()
    for sentence, parse in recipe_parses.iteritems():
      subtrees = parse.subtrees(lambda t: t.label() in nonterminals)
      subtrees_as_list = [t for t in subtrees]
      if len(subtrees_as_list) == length:
        recipe_parses_of_length[sentence] = subtrees_as_list
      
    parses_of_length[recipe] = recipe_parses_of_length
  return parses_of_length

def get_combined_data(commands, parses):
  data = dict()
  for recipe, recipe_commands in commands.iteritems():
    if recipe not in parses.keys():
      continue
    recipe_data = dict()
    recipe_parses = parses[recipe]
    for sentence, sentence_commands in recipe_commands.iteritems():
      if sentence not in recipe_parses.keys():
        continue
      sentence_parses = recipe_parses[sentence]
      datum = [sentence_parses, sentence_commands]
      recipe_data[sentence] = datum
    data[recipe] = recipe_data
  return data

def get_frame_types(data, types = ["NP", "PP", ], verb_types=["VB", "VBP", "VBN"]):
  frame_types = []
  for recipe, recipe_data in data.iteritems():
    for sentence, datum in recipe_data.iteritems():
      tree = datum[0][0]
      command = datum[1][0]

      for vp_tree in tree.subtrees(lambda t: t.label() == "VP"):
        frame = []
        for subtree in vp_tree:
          if subtree.label() in types:
            frame.append(subtree.label())
        verbs = []
        for vb_tree in vp_tree.subtrees(lambda t: t.label() in verb_types):
          verbs.append(vb_tree.leaves()[0])
          break
        frame_item = [verbs[0], frame, sentence]
        frame_types.append(frame_item)
  return frame_types

def count_frame_types(frame_types):
  counts = dict()
  for frame_type in frame_types:
    predicate = frame_type[0]
    frame = frame_type[1]
    if predicate not in counts.keys():
      counts[predicate] = dict()

    frame_key = str(frame)
    if frame_key not in counts[predicate].keys():
      counts[predicate][frame_key] = 0
    counts[predicate][frame_key] += 1
  return counts

def sum_counts(counts):
  summed_counts = dict()
  for predicate, frame_counts in counts.iteritems():
    for frame, count in frame_counts.iteritems():
      if frame not in summed_counts.keys():
        summed_counts[frame] = 0
      summed_counts[frame] += count
  counts_list = []
  for frame, count in summed_counts.iteritems():
    counts_list.append((frame, count))
  return sorted(counts_list, key=lambda item: item[1])

def print_counts(counts):
  counts_list = []
  for predicate, frame_counts in counts.iteritems():
    for frame, count in frame_counts.iteritems():
      counts_list.append((predicate, frame, count))
  sorted_by_count = sorted(counts_list, key=lambda item: item[2] )
  sorted_by_predicate = sorted(sorted_by_count, key=lambda item: item[0])

  for item in sorted_by_predicate:
      print(item[0] + " " + str(item[1]) + ": " + str(item[2]))

  for item in sum_counts(counts):
    print(str(item[0]) + ": " + str(item[1]))

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
  commands_of_length_1 = get_commands_of_length(condensed_commands, 1)

  parses = read_parse_files(parse_files)
  parses_with_one_vp = get_parses_of_length(parses, 1)

  combined_data = get_combined_data(commands_of_length_1, parses_with_one_vp)

  frame_types = get_frame_types(combined_data)
  counts = count_frame_types(frame_types)
  
  print_counts(counts)
