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

    numSections = 0
    sectionLengths = defaultdict(int)

    # all recipes
    for recipe_file in glob('../annotated_recipes/*.xml'):
        
        
        if (random.random() <= testingPercentage):
            testingRecipes.append(recipe_file)
            #continue

        #print recipe_file
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

        curSection = []

        commands = [element.text.split('(', 1)[0] for element in recipe_tree.findall('.//annotation')]
        originals = [element.text for element in recipe_tree.findall('.//originaltext')]

        isLastOneSingleton = False
        pastHeader = False
        for curCmd, curText in zip(commands, originals):

            if (pastHeader == False and curCmd != 'create_ing'):
                pastHeader = True
                
            if (pastHeader == False or curCmd == 'create_ing' or curCmd == 'create_tool'):
                continue

            size = len(curSection)
            if (curText != prevText and size > 0):
                #print curSection
                sectionLengths[size] += 1
                numSections += 1
                curSection = []
            curSection.append(curCmd)
            prevText = curText

        size = len(curSection)
        if (size > 0):
            sectionLengths[size] += 1
            numSections += 1

    for value,key in sorted(sectionLengths.iteritems(), key=operator.itemgetter(1), reverse=True):
       print str(value) + ":" + str(float(key)/float(numSections))

main()
