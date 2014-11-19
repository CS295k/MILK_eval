import sys
sys.path.append('..')

from glob import glob
import MILK_eval

for recipe_file in glob('../annotated_recipes/*.xml'):
	try:
		recipe = MILK_eval.MILK_parse(recipe_file)
		cln = [cmd if cmd[0] == "create_ing" or cmd[0] == "create_tool" else (cmd[0], [cmd_ if isinstance(cmd_, str) else [cmd__ for cmd__ in cmd_ if cmd__.startswith("ing") or cmd__.startswith("t")] for cmd_ in cmd[1] if cmd_ is not None and (isinstance(cmd_, list) or (cmd_.startswith("ing") or cmd_.startswith("t")))]) for cmd in recipe]
		n = "%s.txt" % recipe_file.split("/")[-1].split(".", 1)[0].encode("rot13")
		f = open("../clean_recipes/%s" % n, "w")
		for cmd in cln:
			s = "%s(%s)\n" % (cmd[0], ", ".join([cmd_ if isinstance(cmd_, str) else "[%s]" % ", ".join(cmd_) for cmd_ in cmd[1]]))
			f.write(s.encode("utf-8"))
	except (TypeError, MILK_eval.RecipeException), e:
		print 'Unable to translate %s due to evaluation failure.\n\n\n\n' % recipe_file
		print e
	except Exception, e:
		print 'Unable to translate %s due to translation failure.\n\n\n\n' % recipe_file
		raise