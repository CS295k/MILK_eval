#!/usr/bin/python
#
# written by Chris Tanner
# input: recipes in SourCream (xml) format
# output: # of times each unigram cmd is seen, along w/ how many times it corresponds to the start of a new English Instruction
#         # of times each quad,tri,bigram within Testing was not seen during Training, along w/ how many times the back-offs weren't seen
# notes: i skip over the header of create_ing's

import xml.etree.cElementTree as ET
import fnmatch
import os
import random
import operator
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
    

    unigramSingletonCounts = defaultdict(int) # unused for now?
    unigramSameCounts = defaultdict(int)
    bigramTogetherCounts = defaultdict(int)
    trigramTogetherCounts = defaultdict(int)
    quadTogetherCounts = defaultdict(int)

    unigramStartCounts = defaultdict(int)

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
        prevprevprevCmd = ""

        curText = ""
        prevText = ""
        prevprevText = ""
        prevprevprevText = ""

        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]
        #print "\n\n" + recipe_file

        isLastOneSingleton = False
        pastHeader = False
        for curCmd, curText in zip(commands, originals):



            if (prevCmd != ""):
                # the 1st line of a recipe is always a new line, so we only count the non-1stlines for our stats

                if (pastHeader == False and curCmd != 'create_ing'):
                    pastHeader = True

                if (pastHeader == False):
                    continue


                # represents we found a new section
                if (curText != prevText and prevText != ""):
                    unigramStartCounts[curCmd] += 1

                unigramCounts[curCmd] += 1
                
                bigramCounts[prevCmd,curCmd] += 1
                #if (prevCmd == "create_ing" and curCmd == "create_ing"):
                    #print "*****"

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

            if (prevprevprevCmd != ""):
                # checks if the 4 last cmds corresponded to the same English instruction
                if (prevprevprevText == prevprevText and prevprevText == prevText and prevText == curText):
                    quadTogetherCounts[prevprevprevCmd,prevprevCmd,prevCmd,curCmd] += 1

            prevprevprevCmd = prevprevCmd
            prevprevprevText = prevprevText

            prevprevCmd = prevCmd
            prevprevText = prevText

            prevCmd = curCmd
            prevText = curText

        # checks if the last cmd was a singleton (i.e., text instruction diff. from its neighbors)
        if (isLastOneSingleton):
            unigramSingletonCounts[prevCmd] += 1

    #print "bitogether:", bigramTogetherCounts
    #print "tricounts:", trigramTogetherCounts
    #print "quadcounts:", quadTogetherCounts


    # prints the most common unigram cmds
    print "training size:",(numRecipes-len(testingRecipes))
    #sorted_list = [(k,v) for v,k in sorted([(v,k) for k,v in unigramCounts.items()], reverse=True)]
    #print sorted_list
    tot = 0
    for k in unigramCounts:
        tot += unigramCounts[k]
    print tot

    sing = 0
    for k in unigramStartCounts:
        sing += unigramStartCounts[k]
    print sing

    for value,key in sorted(unigramCounts.iteritems(), key=operator.itemgetter(1), reverse=True):
       print value + ":" + str(key) + " (" + str(float(key)/float(tot)) + "); started a new line: " + str(unigramStartCounts[value]) + " (" + str(float(unigramStartCounts[value])/float(sing)) + ")"
       
    # prints again but in csv format
    for value,key in sorted(unigramCounts.iteritems(), key=operator.itemgetter(1), reverse=True):
       print value + "," + str(key) + "," + str(unigramStartCounts[value])

    # tests our line separation predictions
    # evaluation is merely % accurate with respect to guessing if the current cmd and prev cmd
    # correspond to different lines
    print "testing on " + str(len(testingRecipes)) + " recipes"

    recipeScores = []
    num4grams = 0
    num3grams = 0
    num2grams = 0
    missing4grams = []
    missing43grams = []
    missing3grams = []
    missing32grams = []
    missing2grams = []
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

        curCmdList = []

        pastHeader = False
        for curCmd, curText in zip(commands, originals):

            if (pastHeader == False and curCmd != 'create_ing'):
                pastHeader = True

            if (pastHeader == False):
                continue

            # represents we just finished a section and are starting a new one
            size = len(curCmdList)
            if (curText != prevText and size > 0):

                strlist = tuple(curCmdList)
                if (size == 4):
                    if strlist not in quadTogetherCounts:
                        missing4grams.append(strlist)

                        tmp = []
                        for i in range(0,3):
                            tmp.append(curCmdList[i])
                        strlist2 = tuple(tmp)
                        if strlist2 not in trigramTogetherCounts:
                            missing43grams.append(strlist2)

                    num4grams += 1
                elif (size == 3):
                    if strlist not in trigramTogetherCounts:
                        missing3grams.append(strlist)

                        tmp = []
                        for i in range(0,2):
                            tmp.append(curCmdList[i])
                        strlist2 = tuple(tmp)
                        if strlist2 not in bigramTogetherCounts:
                            missing32grams.append(strlist2)

                    num3grams += 1
                elif (size == 2):
                    if tuple(curCmdList) not in bigramTogetherCounts:
                        missing2grams.append(strlist)
                    num2grams += 1
                curCmdList = []
            curCmdList.append(curCmd)
            prevText = curText
        if (len(curCmdList) > 0):
            size = len(curCmdList)
            strlist = tuple(curCmdList)
            if (size == 4):
                if strlist not in quadTogetherCounts:
                    missing4grams.append(strlist)

                    tmp = []
                    for i in range(0,3):
                        tmp.append(curCmdList[i])
                    strlist2 = tuple(tmp)
                    if strlist2 not in trigramTogetherCounts:
                        missing43grams.append(strlist2)

                num4grams += 1
            elif (size == 3):
                if strlist not in trigramTogetherCounts:
                    missing3grams.append(strlist)

                    tmp = []
                    for i in range(0,2):
                        tmp.append(curCmdList[i])
                    strlist2 = tuple(tmp)
                    if strlist2 not in bigramTogetherCounts:
                        missing32grams.append(strlist2)

                num3grams += 1
            elif (size == 2):
                if tuple(curCmdList) not in bigramTogetherCounts:
                    missing2grams.append(strlist)
                num2grams += 1

    print "we saw",num4grams,"quadgrams:",len(missing4grams),"missing (",str(len(missing43grams)),"back-off tris missing)"
    print "we saw",num3grams,"trigrams:",len(missing3grams),"missing (",str(len(missing32grams)),"back-off bis missing)"
    print "we saw",num2grams,"bigrams:",len(missing2grams),"missing"
'''
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
        
    probs = []
    tmp = defaultdict(float)

    for k,v in bigramTogetherCounts.iteritems():
        prob = float(v)/bigramCounts[k]
        probs.append(prob)
        #print(str(k) + ", " + str(prob))
        tmp[k] = prob
        
    #print(str(sorted(probs)))
    for i in sorted(tmp, key=tmp.get):
        print i,tmp[i]

    print "avg accuracy from line-to-line:",sum(recipeScores)/len(recipeScores)
'''
main()
