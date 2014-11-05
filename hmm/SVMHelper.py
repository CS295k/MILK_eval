#!/usr/bin/python
#
# written by Chris Tanner
# input: recipes in SourCream (xml) format
# output: svm training/testing files
# translaotrepreprocessor6 results: 83.4 fscore on the manual train/test split
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
    
    manualSplit = True

    # random train/test
    recipesDir = '../annotated_recipes/*.xml'
    testingPercentage = 0.1

    # forced train/test
    trainDir = 'train/*xml'
    testDir = 'test/*.xml'

    trainingRecipes = []
    testingRecipes = []
    allRecipes = []
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
    allRecipes.extend(trainingRecipes)
    allRecipes.extend(testingRecipes)

    # collects tokens of all sorts
    uniPrevs = []
    uniAfters = []
    biPrevs = []
    triples = []

    for recipe_file in allRecipes:
        print recipe_file
        with open(recipe_file, 'r') as recipe_xml:
            recipe_tree = etree.XML(recipe_xml.read())

        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]
        prevprevCmd = ""
        prevCmd = "|"
        for curCmd, curText in zip(commands, originals):
            if (curCmd == 'create_ing' or curCmd == 'create_tool'):
                continue

            if (prevprevCmd != ""):
                biprev = prevprevCmd,prevCmd
                triple = prevprevCmd,prevCmd,curCmd
                if (prevCmd not in uniPrevs):
                    print "adding:",prevCmd
                    uniPrevs.append(prevCmd)
                if (curCmd not in uniAfters):
                    uniAfters.append(curCmd)
                if (biprev not in biPrevs):
                    biPrevs.append(biprev)
                if (triple not in triples):
                    triples.append(triple)
            
            prevprevCmd = prevCmd
            prevCmd = curCmd

    # order of training/testing features will be
    # 1 before
    # 1 after
    # 2 before
    # triple
    oneAfterPadding = len(uniPrevs)+1
    biPrevPadding = oneAfterPadding + len(uniAfters)
    triplePadding = biPrevPadding + len(biPrevs)
    print "triple padd+trip" + str(triplePadding + len(triples))
    # makes training and testing for libsvm/liblinear
    ftrain = open('training.txt', 'w')
    ftest = open('testing.txt', 'w')
    ftruth = open('truth.txt', 'w')
    for recipe_file in allRecipes:
        #print recipe_file
        with open(recipe_file, 'r') as recipe_xml:
            recipe_tree = etree.XML(recipe_xml.read())

        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]
        prevprevCmd = ""
        prevCmd = "|"
        prevText = ""
        curSection = []
        #print len(uniPrevs)
        #print len(uniAfters)
        #print len(biPrevs)
        index = 0
        for curCmd, curText in zip(commands, originals):
            if (curCmd == 'create_ing' or curCmd == 'create_tool'):
                continue

            if (prevprevCmd != ""):
                biprev = prevprevCmd,prevCmd
                triple = prevprevCmd,prevCmd,curCmd
                size = len(curSection)
                isBreak = False
                featureInstance = "-1"

                # there's a break the 'prevCmd' and 'curCmd'
                if (curText != prevText and size > 0):
                    isBreak = True
                    featureInstance = "+1"
                    curSection = []
                
                curSection.append(curCmd)
                featureInstance += " " + str(uniPrevs.index(prevCmd)+1) + ":1 " + str(uniAfters.index(curCmd) + oneAfterPadding) + ":1 " + str(biPrevs.index(biprev) + biPrevPadding) + ":1 " + str(triples.index(triple) + triplePadding) + ":1\n"

                if (recipe_file in trainingRecipes):
                    ftrain.write(featureInstance)
                else:
                    # constructs the truth line
                    truth = recipe_file + " " + str(index) + " "
                    if (isBreak):
                        truth += "1 "
                    else:
                        truth += "0 "
                    truth += prevCmd + "," + curCmd + "\n"

                    ftest.write(featureInstance)
                    ftruth.write(truth)
                    
                index += 1
                #print featureInstance
            prevText = curText
            prevprevCmd = prevCmd
            prevCmd = curCmd
    ftrain.close()
    ftest.close()
    ftruth.close()
    exit(1)
    # now i need to go through allRecipes, while looking at cur text,
    # and if there is a break, then it's a pos, otherwise neg,
    # and if curRecipe is in training, then output it to that file
    # if it's not, then output to testing file, along w/ a truth file which is later used for knowing what predictinos go to whcih
    # -- mak ethe truth file have an id ... i need to look at the java version to see what i did
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
