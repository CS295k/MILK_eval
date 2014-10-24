#!/usr/bin/python
#
# written by Chris Tanner
# input: recipes in SourCream (xml) format
# output: f-score using my ad-hoc probabilistic language model approach to determine where breaks occur
# notes: i skip over all create_ing and create_tool cmds
# results: 83.4 fscore on the manual train/test split
#          ~77 fscore when on random 90% train, 10% test (sometimes 73, high of 82) 
import xml.etree.cElementTree as ET
import fnmatch
import os
import random
import operator
from glob import glob
from lxml import etree

from sets import Set
from collections import defaultdict
from eval2 import segmentation_scoring

def main():
    
    manualSplit = False

    # random train/test
    recipesDir = '../annotated_recipes/*.xml'
    testingPercentage = 0.1

    # forced train/test
    trainDir = 'train/*xml'
    testDir = 'test/*.xml'

    trainingRecipes = []
    testingRecipes = []
    
    bigramPadding = .5

    fileToCmds = {}

    # gets the filenames for train/test
    if (manualSplit):
        for recipe_file in glob(trainDir):
            trainingRecipes.append(recipe_file)

        for recipe_file in glob(testDir):
            testingRecipes.append(recipe_file)
    else:
        for recipe_file in glob(recipesDir):
            if (random.random() <= testingPercentage):
                testingRecipes.append(recipe_file)
            else:
                trainingRecipes.append(recipe_file)
    print "testing:",testingRecipes
    fin = open('cmdsOnly.txt', 'r')
    for line in fin:
        tokens = line.split(',')
        curFile = tokens[0]
        curCmds = []
        for cmd in tokens[1:]:
            curCmds.append(cmd.strip())
        fileToCmds[curFile] = curCmds
    fin.close()

    # trains
    numSections = 0
    sectionLengths = defaultdict(int)

    numBigrams = 0
    bigramCounts = defaultdict(int)

    condCounts = defaultdict(lambda: defaultdict(int))
    uniCounts = defaultdict(int)
    #fout = open('cmdsOnly.txt', 'w')
    for recipe_file in trainingRecipes:
        with open(recipe_file, 'r') as recipe_xml:
            recipe_tree = etree.XML(recipe_xml.read())

        prevText = ""
        curSection = []
        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]
        #fout.write(recipe_file)
        for curCmd, curText in zip(commands, originals):

            if (curCmd == 'create_ing' or curCmd == 'create_tool'):
                continue

            #fout.write("," + curCmd)

            # found a new english instr
            size = len(curSection)
            if (curText != prevText and size > 0):
                sectionLengths[size] += 1
                numSections += 1
                curSection.insert(0,"|")
                curSection.append("|")
                
                # counts bigrams
                for i in range(0,len(curSection)-1):
                    first = curSection[i]
                    second = curSection[i+1]
                    bigramCounts[first,second] +=1
                    condCounts[first][second] += 1
                    uniCounts[first] += 1
                    numBigrams +=1

                curSection = []
            curSection.append(curCmd)
            prevText = curText
        #fout.write('\n')
        size = len(curSection)
        if (size > 0):

            sectionLengths[size] += 1
            numSections += 1

            curSection.insert(0,"|")
            curSection.append("|")
            # counts bigrams
            for i in range(0,len(curSection)-1):
                first = curSection[i]
                second = curSection[i+1]
                bigramCounts[first,second] +=1
                condCounts[first][second] += 1
                uniCounts[first] += 1
                numBigrams +=1
                
    print condCounts['do']
    print uniCounts['do']
    #exit(1)

    probSectionLength = []
    probAtLeastLength = []
    for value,key in sorted(sectionLengths.iteritems(), key=operator.itemgetter(1), reverse=True):
        probSectionLength.append(str(float(key)/float(numSections)))

    for i in range(0,len(probSectionLength)):
        print i, probSectionLength[i]

        sum = 0
        for j in range(i,len(probSectionLength)):
            sum += float(probSectionLength[j])
        probAtLeastLength.append(sum)


    print probAtLeastLength

    # tests
    fileToGuesses = {}
    flat_guess = []
    for test in testingRecipes:

        curCmds = fileToCmds[test]
        curGuessSection = []
        guessMarkers = []
        for curCmd in curCmds:
            size = len(curGuessSection)
            if (size > 0):

                # prob no break
                pLength = 0 # initialize variable
                if ((size+1) <= len(probAtLeastLength)):
                    pLength = probAtLeastLength[size] # 0-based indexing (i.e., length of 1 is stored at index 0)
                else:
                    pLength = 0.003 / float(size+1)

                # calculate bigram prob
                pSeq2 = 1
                tmp = list(curGuessSection)
                tmp.insert(0,"|")
                tmp.append(curCmd)
                #print "tmp:", tmp
                for i in range(0, len(tmp)-1):
                    first = tmp[i]
                    second = tmp[i+1]
                    tmpList = []
                    tmpList.append(first)
                    tmpList.append(second)
                    tup = tuple(tmpList)
                    curSeqProb2 = float(condCounts[first][second] + bigramPadding) / float(uniCounts[first])
                    pSeq2 *= curSeqProb2

                pNoBreak = pLength*pSeq2 # change
                
                # prob break
                pLength = 0
                if ((size) <= len(probSectionLength)):
                    pLength = float(probSectionLength[size-1]) # 0-based indexing (i.e., length of 1 is stored at index 0)
                else:
                    pLength = 0.003 / float(size)

                tmp = list(curGuessSection)
                tmp.insert(0,"|")
                tmp.append("|")
                tmp.append(curCmd)
                pSeq2 = 1
                for i in range(0, len(tmp)-1):
                    first = tmp[i]
                    second = tmp[i+1]
                    tmpList = []
                    tmpList.append(first)
                    tmpList.append(second)
                    tup = tuple(tmpList)
                    
                    curSeqProb2 = float(condCounts[first][second] + bigramPadding) / float(uniCounts[first])
                    pSeq2 *= curSeqProb2

                pBreak = pLength*pSeq2 # change

                # make a break!
                if (pBreak >= pNoBreak):
                    for i in range(0,len(curGuessSection)-1):
                        guessMarkers.append(0)
                    guessMarkers.append(1)
                    curGuessSection = []
            curGuessSection.append(curCmd)

        # if we have a remaining section, let's just break at the end
        if (len(curGuessSection) > 0):
            for i in range(0,len(curGuessSection)-1):
                guessMarkers.append(0)
            guessMarkers.append(1)
        
        flat_guess.extend(guessMarkers)
        fileToGuesses[test] = guessMarkers

    flat_truth = []
    for recipe_file in testingRecipes:
        with open(recipe_file, 'r') as recipe_xml:
            recipe_tree = etree.XML(recipe_xml.read())

        prevText = ""
        curTrueSection = []
        truthMarkers = []

        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]
        for curCmd, curText in zip(commands, originals):

            if (curCmd == 'create_ing' or curCmd == 'create_tool'):
                continue

            # true break
            size = len(curTrueSection)
            if (curText != prevText and size > 0):

                for i in range(0, len(curTrueSection)-1):
                    truthMarkers.append(0)
                truthMarkers.append(1)
                curTrueSection = []

            prevText = curText
            curTrueSection.append(curCmd)
        
        if (len(curTrueSection) > 0):
            for i in range(0, len(curTrueSection)-1):
                truthMarkers.append(0)
            truthMarkers.append(1)

        flat_truth.extend(truthMarkers)
        print "----\nrecipe_file",recipe_file
        print "truth:",truthMarkers
        print "guess:",fileToGuesses[recipe_file]

    print segmentation_scoring(flat_truth,flat_guess)
main()
