#!/usr/bin/python
#
# written by Chris Tanner
# input: recipes in SourCream (xml) format
# output: prediction/accuracy of each non-'create_ing' cmd corresponding to a diff English recipe line from that of the prev cmd
# notes: i'm using ad-hoc weights between the trigram, bigram, and unigram models
#        i never write python; hence, the weird program structure;

import xml.etree.cElementTree as ET
import fnmatch
import os
import random
from glob import glob
from lxml import etree

from sets import Set
from collections import defaultdict

def main():
    dataInputDir = '../annotated_recipes/'
    testingPercentage = .10

    unigramCounts = defaultdict(int)
    bigramCounts = defaultdict(int)
    trigramCounts = defaultdict(int)
    
    unigramSingletonCounts = defaultdict(int) # unused for now
    unigramSameCounts = defaultdict(int)
    bigramTogetherCounts = defaultdict(int)
    trigramTogetherCounts = defaultdict(int)

    numRecipes = 0
    testingRecipes = []

    numTexts = 0 # how many non-1st lines we have
    numNewTexts = 0 # how many times the line differs from the prev line (regardless of cmd)

    probPadding = 0.001

    for recipe_file in glob('../annotated_recipes/*.xml'):
        
        if (random.random() <= testingPercentage):
            testingRecipes.append(recipe_file)
            continue

        numRecipes += 1
        with open(recipe_file, 'r') as recipe_xml:
            recipe_tree = etree.XML(recipe_xml.read())

        # keeps track of the last 3 cmds/texts
        curCmd = ""
        prevCmd = ""
        prevprevCmd = ""
        curText = ""
        prevText = ""
        prevprevText = ""

        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]
        #print "\n\n" + recipe_file

        isLastOneSingleton = False
        for curCmd, curText in zip(commands, originals):
            
            if (prevCmd != ""):
                # the 1st line of a recipe is always a new line, so we only count the non-1stlines for our stats
                unigramCounts[curCmd] += 1
                
                bigramCounts[prevCmd,curCmd] += 1
                if (prevCmd == "create_ing" and curCmd == "create_ing"):
                    print "*****"

                # checks if the 2 last cmds corresponded to the same English instruction
                if (prevText == curText):
                    bigramTogetherCounts[prevCmd,curCmd] += 1
                    unigramSameCounts[curCmd] += 1
                else:
                    isLastOneSingleton = True
                    numNewTexts += 1

                # checks if the last cmd was a singleton (i.e., text instruction different from its neighbors)
                if (prevText != curText and prevprevText != prevText):
                    unigramSingletonCounts[prevCmd] += 1

                numTexts += 1

            if (prevprevCmd != ""):
                trigramCounts[prevprevCmd,prevCmd,curCmd] += 1

                # checks if the 3 last cmds corresponded to the same English instruction
                if (prevprevText == prevText and prevText == curText):
                    trigramTogetherCounts[prevprevCmd,prevCmd,curCmd] += 1

            prevprevCmd = prevCmd
            prevprevText = prevText
            prevCmd = curCmd
            prevText = curText

        # checks if the last cmd was a singleton (i.e., text instruction diff. from its neighbors)
        if (isLastOneSingleton):
            unigramSingletonCounts[prevCmd] += 1



    # tests our line separation predictions
    # evaluation is merely % accurate with respect to guessing if the current cmd and prev cmd
    # correspond to different lines
    print "testing on " + str(len(testingRecipes)) + " recipes"

    recipeScores = []
    for recipe_file in testingRecipes:

        print recipe_file

        with open(recipe_file, 'r') as recipe_xml:
            recipe_tree = etree.XML(recipe_xml.read())

        # keeps track of the last 3 cmds/texts
        curCmd = ""
        prevCmd = ""
        prevprevCmd = ""
        curText = ""
        prevText = ""
        prevprevText = ""
        
        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]
        
        numLines = 0
        numCorrect = 0

        # we calculate the probability of the current cmd being generated from the same line of English as the prev line
        for curCmd, curText in zip(commands, originals):
            
            # we ignore the 1st line of each recipe, as that will always be a new line
            if (prevCmd != "" and curCmd != "create_ing"):
                numLines += 1
                prob = 0

                # tries the trigram approach
                if (prevprevCmd == prevCmd and trigramCounts[prevprevCmd,prevCmd,curCmd] != 0):
                    trigramProb = (probPadding + trigramTogetherCounts[prevprevCmd,prevCmd,curCmd]) / trigramCounts[prevprevCmd,prevCmd,curCmd]
                    bigramProb = (probPadding + bigramTogetherCounts[prevCmd,curCmd]) / bigramCounts[prevCmd,curCmd]
                    unigramProb = (probPadding + unigramSameCounts[curCmd]) / unigramCounts[curCmd]
                    prob = .6*trigramProb + .35*bigramProb + 0.5*unigramProb

                elif (bigramCounts[prevCmd,curCmd] != 0):
                    bigramProb = (probPadding + bigramTogetherCounts[prevCmd,curCmd]) / bigramCounts[prevCmd,curCmd]
                    unigramProb = (unigramSameCounts[curCmd] / unigramCounts[curCmd])
                    prob = .95*bigramProb + .05*unigramProb

                else:                    
                    prob = (unigramSameCounts[curCmd] / unigramCounts[curCmd])
                    
                # probability that we say it came from the same line as the prev cmd
                rand = random.uniform(0,1)
                #if (rand <= prob):
                    #print "SAME"
                #else:
                    #print "DIFF"
                if (rand <= prob and prevText == curText):
                    numCorrect +=1
                    #print "\tcorrect"
                elif (rand > prob and prevText != curText):
                    numCorrect +=1
                    #print "\tcorrect"

            prevprevCmd = prevCmd
            prevprevText = prevText
            prevCmd = curCmd
            prevText = curText

        recipeScores.append(float(numCorrect)/numLines)
    print "avg accuracy from line-to-line:",sum(recipeScores)/len(recipeScores)

main()
