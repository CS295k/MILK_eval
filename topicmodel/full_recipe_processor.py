import sys
import json
from porter_stemmer import PorterStemmer
import string
import re


def tokenize(text, stop_word_list):
    token_list = []
    word_list = re.split("\s+", str.lower(text))
    for word in word_list:
        if (word == ""): continue
        stem_word = PorterStemmer().stem(word, 0, len(word)-1)
        stem_word = "".join(c for c in stem_word if c not in string.punctuation)
        if (stem_word == ""): continue
        if (stem_word in stop_word_list): continue
        token_list.append(stem_word)
    return token_list

'''
Tokenize all recipes & save them as individual files
'''
def recipe_process(recipes_path, write_dir):

    stop_word_list = ['a','an','and','are','as','at','be','by','for','from','has', \
                      'he','in','is','it','its','of','on','that','the','to','was', \
                      'were','will','with']
    
    ukn_file_index = 0

    recipes_file = open(recipes_path)
    if not (write_dir.endswith("/")): write_dir += "/"
    recipe_title = ""
    recipe_token_list = []
    for recipes_line in recipes_file:
        ###############
        #print recipes_line
        ###############
        recipes_line = re.sub("\\\\u....", "", recipes_line)
        recipe_item = json.loads(recipes_line)
        if ("title" in recipe_item):
            recipe_title_list = recipe_item["title"]
            if not recipe_title_list: continue
            recipe_title = recipe_title_list[0].encode("utf-8").strip().lower()
        elif ("ingredient" in recipe_item):
            recipe_ing_list = recipe_item["ingredient"]
            if not recipe_ing_list: continue
            recipe_ing = recipe_ing_list[0].encode("utf-8")
            token_list = tokenize(recipe_ing, stop_word_list)
            for token in token_list: recipe_token_list.append(token)
        elif ("step" in recipe_item):
            recipe_step_list = recipe_item["step"]
            if not recipe_step_list: continue
            recipe_step = recipe_step_list[0].encode("utf-8")
            token_list = tokenize(recipe_step, stop_word_list)
            for token in token_list: recipe_token_list.append(token)
        elif ("end_of_recipe" in recipe_item):
            # Write to file
            if (recipe_title == ""):
                recipe_title = "unknown_" + str(ukn_file_index)
                ukn_file_index += 1
            else:
                recipe_title = "_".join(re.split("\s+", recipe_title.replace("/", "_")))
            new_recipe_file_path = write_dir + recipe_title
            new_recipe_file = open(new_recipe_file_path, "w")
            new_recipe_file.write(" ".join(recipe_token_list))
            new_recipe_file.close()
            recipe_title = ""
            recipe_token_list = []
            
    recipes_file.close()

if __name__ == "__main__":
    
    #E.g
    #recipes_path = "../full_recipes2_cleaned.jsonlines.fixed"
    recipes_path = "./full_recipes2_tmp"
    write_path = "./full_recipes/"
    recipe_process(recipes_path, write_path)
