#!/usr/bin/python
#
# written by Chris Tanner, Qi, Eugene Charniak, Spencer Caplan
import xml.etree.cElementTree as ET
import fnmatch
import os
import os.path
import random
import operator
import copy
from glob import glob
from JITDecoders import *
from group_tagger import group_tagger
from probs_new import *
from sklearn.cross_validation import train_test_split
from collections import defaultdict
from MILKChunk import *
from RecipeTranslation import *
from Case_Frame_Helper import *
from MILK_parse import MILK_parse, MILK_parse_command
from NP_generator import gen_NP, file_reader

def strip(recipes):
    # strip loaded recipes to a list of (english, predicate_list)
    # remove create_ing & create_tool
    strip_recipes = map(remove_create_tool_from_commands,
                        map(remove_create_ing_from_commands,
                            map(parseAsCommands, recipes)))
    return strip_recipes

def strip_original_recipes_to_names(recipes):
    strip_recipes = map(remove_create_tool,
                        map(remove_create_ing,
                            map(strip_to_predicate, recipes)))
    return strip_recipes

def strip_to_names(recipes):
    strip_recipes = map(strip_to_predicate_from_commands, recipes)
    return strip_recipes

def parseAsCommands(recipe):
    return [(ot, [MILK_parse_command(x) for x in anns]) for ot, anns in recipe]

def getPreds(recipes):
    # strip loaded recipes to a list of predicate_list
    # remove create_ing & create_tool
    strip_recipes = strip_to_names(strip(recipes))
    preds_list = [[ a for (ot, anns) in strip_recipe for a in anns ] \
                  for strip_recipe in strip_recipes ]
    return preds_list

# this method is broken; doesn't work
def getEngs(recipes):
    # strip loaded recipes to a list of english_list
    # remove create_ing & create_tool
    strip_recipes = strip_to_names(strip(recipes))
    eng_list = [[ a for (ot, anns) in strip_recipe for a in ot ] \
                  for strip_recipe in strip_recipes ]
    return eng_list

def getCommands(recipes):
    strip_recipes = strip(recipes)
    commandsList = [[ a for (ot, anns) in strip_recipe for a in anns ] \
                  for strip_recipe in strip_recipes ]
    return commandsList

# takes a recipe file (e.g., ../annotated_recipes/Alisons-Slow-Cooker-Vegetable-Beef-Soup.rcp_tagged.xml)
def loadVerbMarkers(input):

    verbMarkersDict = defaultdict(tuple)
    f = open(input, 'r')
    
    # list of tuples (verbMarkers,prob) for the current tuple
    # (e.g., 0,4; representing sanning the first 4 milk cmds)
    curList = [] 

    curTuple = ()

    for line in f:
        tokens = line.strip().split(" ")

        # represents a new tuple/span
        if (len(tokens) == 3):

            # we've finished a tuple, so let's store it
            if (curTuple != ()):
                print "setting",curTuple,"->",curList
                verbMarkersDict[curTuple] = curList
                curList = []
            curTuple = (tokens[0],tokens[1])
        elif (len(tokens) == 2):
            prob = (tokens[1],float(tokens[0])) # format is (0101, probability)
            curList.append(prob)

    # finishes file
    verbMarkersDict[curTuple] = curList
    print "setting",curTuple,"->",curList
    #print verbMarkersDict
    return verbMarkersDict

# takes a file which lists all of spencer's probs (e.g., 10FoldCrossValidation_verbGenerationProbabilities)
def loadVerbProbs(input):

    verbDict = defaultdict(list)
    f = open(input, 'r')

    curRecipe = ""
    curList = []
    curDict = defaultdict(float)
    curCmdNum = 0
    for line in f:
        if line.startswith("./annotated"):
            # print "found recipe:",line
            curCmdNum = 0
            curDict = defaultdict(float)

            # represents we've finished reading a recipe
            if (curRecipe != "" and len(curList) > 0):
                verbDict[curRecipe] = curList

                #print 'curRecipe:', curRecipe, "has preds", len(curList)
                #for i in curList:
                #    print "* ", i

                curList = []

            curRecipe = "." + line.strip()
        elif (line.strip() != ""):
            tokens = line.strip().split(" ")
            pred = tokens[0]
            verb = tokens[len(tokens)-2]
            prob = float(tokens[len(tokens)-1])
            if (verb != "noverb" and len(curDict.keys()) == 0):
                curDict[verb] = prob

        # represents an empty line
        else:
            if (len(curDict) > 0):
                curList.append(curDict)
                curDict = defaultdict(float)
                curCmdNum += 1
    
    # finishes/saves the last recipe            
    if (curRecipe != "" and len(curList) > 0):
        verbDict[curRecipe] = curList

    return verbDict

def getEnglishRecipes(train_recipes, test_recipes, mod):


    
    ############
    # To use
    # If state_probs is None, then finish
    # select(state) given state_probs[state]=0 might cause problems later

    group_num = 4
    best_seq_num = 100

    preds = getPreds(test_recipes)
    commands = getCommands(test_recipes)
    engs = getEngs(test_recipes)

    # iterates through each test recipe
    for i in xrange(0,len(test_recipes)):
  
        recipe_name = test_paths[i]
        print recipe_name
        #if (recipe_name != "../annotated_recipes/Bakers-Secret-Pie-Crust.rcp_tagged.xml"):
        #    continue
        curPreds = preds[i]
        curCommands = commands[i]
        #print "curPreds:",curPreds
        #print "finished pos =",str(len(curPreds))
        # gets eugene's verb markers for the current recipe
        # constructs the filename
        #vmFile = recipe_name[recipe_name.rfind('/')+1:][:-15] # works for mac/linux
        vmFile = recipe_name[recipe_name.rfind('/')+1:][18:-15] # works for windows
        curVerbMarkerMasks = loadVerbMarkers(verbMarkersDir + vmFile)
        #print "cvm"
        #for k in curVerbMarkerMasks.keys():
        #    print k,curVerbMarkerMasks[k]
        #print "cvm:",curVerbMarkerMasks

        # gets spencer's stored verb probs for the current recipe
        #curVerbProbs = verbProbs[recipe_name] # works for mac/linux
        curVerbProbs = verbProbs[recipe_name.replace("\\", "/")] # works for windows
        #print "verb probs:", curVerbProbs
        #print "len of verbprobs from spencer",len(curVerbProbs)

        # represents that spencer's file doesn't have probabilities for it
        if (len(curVerbProbs) == 0):
            print "*** spencer's file doesn't have data for current recipe!"
            continue
        completedRecipes = []
        candidateRecipes = [] # incomplete recipes -- still exploring all possible paths
         
        # constructs our first, empty RecipeTranslation
        rt = RecipeTranslation()
        candidateRecipes.append(rt)

        while (len(candidateRecipes) > 0):

            newCandidates = []
            for curCandidate in candidateRecipes:

                # constructs a new hmm group tagger
                train_with_only_predicate_names = strip_original_recipes_to_names(train_recipes)
                test_with_only_predicate_names = strip_original_recipes_to_names(test_recipes)
                tagger = group_tagger(train_with_only_predicate_names, test_with_only_predicate_names)
                jit_decoder = tagger.get_JITDecoder(i, group_num, best_seq_num)

                last_marker = 0
                # takes the path of the curCandidate
                for each_marker in curCandidate.predMarkers:
                    #print "pred marker:",each_marker

                    # Qi -- CHANGE THE LINE BELOW to be 1-based, i.e.:
                    # step_size = each_marker - last_marker
                    step_size = each_marker - last_marker - 1 # the -1 makes it 0-based
                    #print "\ttaking step:",step_size

                    #state_probs = jit_decoder.ping();
                    #print state_probs
                    #jit_decoder.select(2);

                    jit_decoder.select(step_size)
                    last_marker = each_marker

                # gets Qi's (#-of-milk-pred)-to-(1-engStatement) probabilities for the current state
                # e.g., [.5, .2, .1, .3] means there's a .3 chance of 4 milk preds mapping to 1 eng instr
                state_probs = jit_decoder.ping()
                #print "*** last_marker/curHead:",last_marker,";state_probs",state_probs

                # tries each of the 4 possible state transitions (i.e., 1 state, 2 states, .. 4 states)
                for num_states in xrange(1,5):
                    #print "considering:",(last_marker,last_marker+num_states)
                    tup = (str(last_marker),str(last_marker+num_states))
                    #print "verbMarker paths:",curVerbMarkerMasks[tup]

                    # ignores impposible states, along w/ handle's eugene's error of having
                    # tuples (probabilities/masks) that correspond to indices that are out of
                    # bounds (e.g., 12 13 1 when really there are only 12 milk cmds for the recipe)
                    if (last_marker+num_states > len(curPreds)):
                        break

                    # skip over states which the HMM outputs as having 0 probability
                    if (state_probs[num_states-1] == 0):
                        #print "*** skipping state",str(num_states-1),"while at head pos",str(last_marker)
                        continue

                    for verbMarkerMask in curVerbMarkerMasks[tup]:
#
                        #print "trying",verbMarkerMask
                        verbFlags = verbMarkerMask[0]
                        #print "vf", verbFlags
                        curProb = math.log(verbMarkerMask[1]) + math.log(0.00001+state_probs[num_states-1]) # TODO: OK to add 0.00001?
                        #print "curProb:",curProb

                        comms = []
                        predNums = []
                        verbs = []
                        for flagPos in xrange(0,len(verbFlags)):
                            #print "flagpos",flagPos,verbFlags[flagPos]
                            predIndex = last_marker + flagPos
                            #print "predIndex",predIndex,curPreds[predIndex]
                            comms.append(curCommands[predIndex])
                            predNums.append(predIndex)

                            # if verb flag is 1, then let's multiple/accumulate our prob by the most-likely verb prob
                            if (verbFlags[flagPos] == '1'):
                                #print "bestverb",curVerbProbs[predIndex]
                                if len(curVerbProbs[predIndex].keys()) > 0: # TODO: is this right???
                                    bestVerb = curVerbProbs[predIndex].keys()[0]
                                    verbs.append(bestVerb)

                                #print "prob:",curVerbProbs[predIndex][bestVerb]
                                    curProb += math.log(curVerbProbs[predIndex][bestVerb])
                                else:
                                    print "****** ERROR!!! curVerbProbs doesn't have right stuff:"
                                    print curVerbProbs
                                    exit(1)
                        #print "*** prob for mask:",verbMarkerMask,":",curProb

                        # makes a new MILKChunk for the current span attempt
                        mc = MILKChunk(comms, predNums, curProb, verbFlags, verbs)

                        #print mc

                        newHead = last_marker + num_states
                        newRT = copy.deepcopy(curCandidate)
                        newRT.addMILKChunk(mc, newHead, curProb)
                        #print newRT

                        # represents we've reached the end; no more MILK predicates remaining,
                        # so this newly made RecipeTranslation will be 'completed'
                        # and not added to the queue
                        if (newHead == len(curPreds)):
                            completedRecipes.append(newRT)
                        elif (newHead < len(curPreds)):
                            newCandidates.append(newRT)
                        else:
                            print "*** ERROR: we went beyond the # of milk cmds?!"
                            exit(1)
            #exit(1)
            candidateRecipes = []
            candidateRecipes = copy.deepcopy(newCandidates)
            print "now our # of candidates:", str(len(candidateRecipes)), "# complete:", str(len(completedRecipes))
            # if (len(candidateRecipes)-len(completedRecipes)) > 500:# and len(completedRecipes) > 10:
                # "&&& too many candidates, so stopping prematurely"
                # break
        if len(completedRecipes) > 0:
            file_reader()
            sortedPaths = sorted(completedRecipes, key=lambda rt: rt.totalProb, reverse=True)
            print "\n\n"
            ingDescriptions, toolDescriptions = seedDescriptions(recipe_name)
            recipeLines = []
            for milkChunk in sortedPaths[0].milkChunks:
                nouns = getNounsFromCommands(milkChunk.commands, ingDescriptions, toolDescriptions)
                caseFrameProbabilities = probabilitiesFromFile(os.path.join("..", "Case_Frame_Probabilities.txt"))
                topLevelProbabilities = probabilitiesFromFile(os.path.join("..", "Top_Level_Probabilities.txt"))
                recipeLines.append(inputToEnglish(None, milkChunk.verbs, nouns, caseFrameProbabilities, topLevelProbabilities))
                updateIngredientDescriptions(milkChunk.commands, ingDescriptions, mod)
            filename = os.path.basename(recipe_name)[:-15] + ".txt"
            sendToOutputEnglishFile("\n".join(recipeLines), filename)
            print "\n=============================\n"
        print "done w/ the recipe... exiting"
        #exit(1)
    #jit_decoder = tagger.get_JITDecoder(test_recipe_index, group_num, best_seq_num)
    #state_probs = jit_decoder.ping();
    #print state_probs
    #jit_decoder.select(2);
    #state_probs = jit_decoder.ping();
    #print state_probs
    ############

def seedDescriptions(filename):
    commands = MILK_parse(filename)
    ingDescriptions = {}
    toolDescriptions = {}
    for command in commands:
        if command[0] == "create_ing":
            ingDescriptions[command[1][0]] = command[1][1]
        elif command[0] == "create_tool":
            toolDescriptions[command[1][0]] = command[1][1]
    return ingDescriptions, toolDescriptions

def updateIngredientDescriptions(commands, ingDescriptions, mod):
    for command in commands:
        inputs = getInputIngredients(command[0], command[1])
        outputs = getOutputIngredients(command[0], command[1])
        if len(inputs) > 0 and len(outputs) > 0:
            if command[0] == "separate":
                assert(len(inputs) == 1)
                gen_NP_result = gen_NP(command[0], ingDescriptions[inputs[0]], mod)
                newNps = gen_NP_result[0][0].split("; ") if "; " in gen_NP_result[0][0] else [gen_NP_result[0][0]]*2
                assert(len(newNps) == 2)
            elif command[0] == "combine":
                gen_NP_result = gen_NP(command[0], "*".join(ingDescriptions[input] for input in inputs), mod)
                newNps = [gen_NP_result[0][0]]
            else:
                assert(len(inputs) == 1)
                gen_NP_result = gen_NP(command[0], ingDescriptions[inputs[0]], mod)
                newNps = [gen_NP_result[0][0]]
            for i in xrange(len(newNps)):
                ingDescriptions[outputs[i]] = newNps[i]

def sendToOutputEnglishFile(outputString, filename):
    file = open(os.path.join(os.path.join("..", "English_Translations"), filename), "w")
    file.write(outputString.encode("utf8"))

if __name__ == "__main__":

    verbMarkersDir = ("../stage2Ps/")
    data_files = glob("../annotated_recipes/*.xml")
            
    # loads spencer's most likely verbs
    verbProbs = loadVerbProbs("10FoldCrossValidation_verbGenerationProbabilities.txt")
    #print "vp:", verbProbs

    len_data_files = len(data_files)
    
    #mc = MILKChunk(25,20)
    #print mc
    #mc.dostuff()
    #print mc
    #exit(1)

    for i in xrange(0, 10):
        print i
        train_paths = []
        test_paths = []
        for j in xrange(len_data_files):
            if ((j+1) % 10 == i):
                test_paths.append(data_files[j])
            else:
                train_paths.append(data_files[j])

        train_recipes = load_recipes(train_paths)
        test_recipes = load_recipes(test_paths)
        
        print len(train_recipes),len(test_recipes)
        print len(train_paths),len(test_paths)

        english_text = getEnglishRecipes(train_recipes, test_recipes, i)
        # exit(1)
        
    
