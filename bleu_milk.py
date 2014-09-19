import bleu
from glob import glob
import MILK_eval
import MILK_parse
import scripts.recipe2text1 as recipe2text

ref_texts = []
translations = []
for recipe_file in glob('annotated_recipes/*.xml'):
	# print recipe_file

	try:
		recipe = MILK_eval.MILK_eval(recipe_file)
		# print recipe[1:]

		original_text = MILK_parse.MILK_parse_originaltext(recipe_file)
		generated_text = recipe2text.RecipeToText(recipe)

		assert len(original_text) == len(generated_text)

		ref_text, translated = zip(*[(ot, gt) for ot, gt, r in zip(original_text, generated_text, recipe[1:]) if r[0][0] != 'create_tool' and r[0][0] != 'create_ing'])
		ref_texts += [[r] for r in ref_text]
		translations += translated

		for r, t in zip(ref_text, translated):
			print r, '\t', t

		print '\n\n\n'
	except (TypeError, MILK_eval.RecipeException), e:
		print 'Unable to translate %s due to evaluation failure.\n' % recipe_file
		print e
	except Exception, e:
		print 'Unable to translate %s due to translation failure.\n' % recipe_file
		print e

print bleu.score_set(translations, ref_texts)
