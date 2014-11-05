#!/usr/bin/python
#
# written by Chris Tanner, Qi, 
import xml.etree.cElementTree as ET
import fnmatch
import os
import random
import operator
from glob import glob
from JITDecoder import JITDecoder
from group_tagger import group_tagger
from sklearn.cross_validation import train_test_split

if __name__ == "__main__":

    data_files = glob("../annotated_recipes/*.xml")
    train_paths, test_paths = train_test_split(data_files, test_size=0.25)
    
    tagger = group_tagger(train_paths, test_paths)
    
    ############
    # To use
    test_recipe_index = 0
    group_num = 4
    best_seq_num = 100
    jit_decoder = tagger.get_JITDecoder(test_recipe_index, group_num, best_seq_num)
    jit_decoder.ping();
    jit_decoder.select(2);
    jit_decoder.ping();
    ############
    
