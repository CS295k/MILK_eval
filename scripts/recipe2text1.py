import sys
sys.path.append('..')

from glob import glob
import MILK_eval


def IsNull(value):
	return value is None or value == '' or value == 'null'

def RecipeToText(recipe):
	"""Takes a recipe evaluated from MILK_eval and returns a list of strings
	produced by a very simple baseline rule-based approach."""

	out = []
	world = None
	for (annotation, next_world) in recipe[1:]:
		command = annotation[0]
		arguments = annotation[1]

		recipe_text = ''
		if command == 'create_ing':
			# TODO: When computing BLEU score, we may wish to ignore create_ing
			# commands since they are trivially translated
			recipe_text += '%s.' % arguments[1]

		elif command == 'create_tool':
			# TODO: This is a horrible hack but we need some way to make sure that the
			# length of the outputted string is equal to that of the list of original
			# texts.
			recipe_text = '<create_tool>'

		elif command == 'combine':
			recipe_text += 'Combine '

			recipe_text += ', '.join([world.I_d[ing] for ing in arguments[0]])

			if not IsNull(arguments[3]):
				recipe_text += ', %s' % arguments[3]

			recipe_text += '.'

		elif command == 'separate':
			recipe_text += 'Separate '
			recipe_text += '%s and %s' % (world.I_d[arguments[0]], next_world.I_d[arguments[1]])

			if not IsNull(arguments[5]):
				recipe_text += ', %s' % arguments[5]

			recipe_text += '.'

		elif command == 'put':
			recipe_text += 'Put %s in %s. ' % (world.I_d[arguments[0]], world.T_d[arguments[1]])

		elif command == 'remove':
			recipe_text += 'Remove %s from %s. ' % (world.I_d[arguments[0]], world.T_d[arguments[1]])

		elif command == 'cut':
			recipe_text += 'Chop %s' % world.I_d[arguments[0]]

			if not IsNull(arguments[1]):
				recipe_text += ' with %s' % world.T_d[arguments[1]]

			if not IsNull(arguments[4]):
				recipe_text += ', %s' % arguments[4]

			recipe_text += '.'

		elif command == 'mix':
			recipe_text += 'Mix %s' % world.I_d[arguments[0]]

			if not IsNull(arguments[1]):
				recipe_text += ' with %s' % world.T_d[arguments[1]]

			if not IsNull(arguments[4]):
				recipe_text += ', %s' % arguments[4]

			recipe_text += '.'

		elif command == 'cook':
			recipe_text += 'Cook %s' % world.I_d[arguments[0]]

			if not IsNull(arguments[1]):
				recipe_text += ' with %s' % world.T_d[arguments[1]]

			if not IsNull(arguments[4]):
				recipe_text += ', %s' % arguments[4]

			recipe_text += '.'

		elif command == 'do':
			recipe_text += 'Taking %s' % world.I_d[arguments[0]]

			if not IsNull(arguments[1]):
				recipe_text += ' with %s' % world.T_d[arguments[1]]

			if not IsNull(arguments[4]):
				recipe_text += ', %s' % arguments[4]

			recipe_text += '.'

		elif command == 'serve':
			recipe_text += 'Serve %s' % world.I_d[arguments[0]]

			if not IsNull(arguments[1]):
				recipe_text += ', %s' % arguments[1]

			recipe_text += '.'

		elif command == 'set':
			recipe_text += 'Set %s on %s. ' % (world.T_d[arguments[0]], arguments[1])

		elif command == 'leave':
			recipe_text += 'Leave %s' % world.I_d[arguments[0]]

			if not IsNull(arguments[1]):
				recipe_text += ', %s' % arguments[1]

			recipe_text += '.'

		elif command == 'chefcheck':
			recipe_text += 'Check %s for %s. ' % (world.I_d[arguments[0]], arguments[1])

		world = next_world
		out.append(recipe_text)

	return out

# for recipe_file in glob('annotated_recipes/*.xml'):
# 	print recipe_file
#
# 	try:
# 		recipe = MILK_eval.MILK_eval(recipe_file)
# 		print RecipeToText(recipe)
# 		print '\n\n\n'
# 	except (TypeError, MILK_eval.RecipeException), e:
# 		print 'Unable to translate %s due to evaluation failure.\n\n\n\n' % recipe_file
# 		print e
# 	except Exception, e:
# 		print 'Unable to translate %s due to translation failure.\n\n\n\n' % recipe_file
# 		raise
