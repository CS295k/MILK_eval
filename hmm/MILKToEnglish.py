#!/usr/bin/python
#
# written by Chris Tanner, Qi, 
import xml.etree.cElementTree as ET
import fnmatch
import os
import random
import operator
from glob import glob
from JITDecoders import *
from group_tagger import group_tagger
from probs_new import *
from sklearn.cross_validation import train_test_split


def strip(recipes):

    # strip loaded recipes to a list of (english, predicate_list)
    # remove create_ing & create_tool

    strip_recipes = map(remove_create_tool,
                        map(remove_create_ing,
                            map(strip_to_predicate, recipes)))
    return strip_recipes

def strip2(recipes):

    # strip loaded recipes to a list of predicate_list
    # remove create_ing & create_tool

    strip_recipes = strip(recipes)
    preds_list = [[ a for (ot, anns) in strip_recipe for a in anns ] \
                  for strip_recipe in strip_recipes ]
    return preds_list


def getEnglish(train_recipes, test_recipes):

    # Get hmm group tagger
    tagger = group_tagger(strip(train_recipes), strip(test_recipes))
    
    ############
    # To use
    # If state_probs is None, then finish
    # select(state) given state_probs[state]=0 might cause problems later
    test_recipe_index = 0
    group_num = 4
    best_seq_num = 100
    jit_decoder = tagger.get_JITDecoder(test_recipe_index, group_num, best_seq_num)
    state_probs = jit_decoder.ping();
    print state_probs
    jit_decoder.select(2);
    state_probs = jit_decoder.ping();
    print state_probs
    ############
    
    
if __name__ == "__main__":

    data_files = glob("../annotated_recipes/*.xml")
    len_data_files = len(data_files)

    for i in xrange(1, 10):
        train_paths = []
        test_paths = []
        for j in xrange(len_data_files):
            if ((j+1) % (i+1) == 0):
                test_paths.append(data_files[j])
            else:
                train_paths.append(data_files[j])
            
        train_recipes = load_recipes(train_paths)
        test_recipes = load_recipes(test_paths)
        english_text = getEnglish(train_recipes, test_recipes)
        
    
