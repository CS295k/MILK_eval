# MILK Recipe Evaluator Runner

# Written by Frank Goodman (fgoodman)
# 9/9/14

from MILK_eval import MILK_eval, RecipeException

from glob import glob
from sys import argv

if __name__ == "__main__":
  success = 0
  fail = 0

  for recipe in glob("annotated_recipes/*.xml"):
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
