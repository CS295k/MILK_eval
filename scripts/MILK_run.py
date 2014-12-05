# MILK Recipe Evaluator Runner

# Written by Frank Goodman (fgoodman)
# 9/9/14

from MILK_eval import MILK_eval, RecipeException

from glob import glob
from sys import argv
import os

###############################################
# Usage:
# python MILK_run.py
# python MILK_run.py file1 file2 ... fileN
# python MILK_run.py dir1 file1 ... dirN fileN
###############################################

if __name__ == "__main__":
  success = 0
  fail = 0
  files = []
  if (len(argv) > 1):
    for path in argv[1:]:
      if os.path.isfile(path):
        files.append(path)
      elif os.path.isdir(path):
        files.extend(glob(path + "/*.xml"))
  else:
    files = glob("annotated_recipes/*.xml")
  for recipe in files:
    try:
      MILK_eval(recipe)
      success += 1
      # print recipe, "was successfully evaluated!" # comment this back in if you want to print output for successful evaluations
    except RecipeException, e:
      fail += 1
      print recipe, "was unsuccessfully evaluated with the following exception:"
      print e
      print ""
    except TypeError, e:
      fail += 1
      print recipe, "was unsuccessfully evaluated with the following exception (possibly due to bad parsing):"
      print e
      print ""
    except:
      print recipe, "produced an unusual exception:"
      raise

  print "Successful evaluations:", success
  print "Failed evaluations:", fail
  print "Total evaluations:", success + fail
