class Recipe(object):

	def __init__(self, title):
		self.title = title
		self.ingredients = []
		self.steps = []

	def addIngredient(self, ingredient):
		self.ingredients.append(ingredient)

	def addStep(self, step):
		self.steps.append(step)

	def __repr__(self):
		out = ""
		out += "Title: %s\n" % self.title
		if self.ingredients:
			out += "Ingredients: %s\n" % self.ingredients[0]
			for ingredient in self.ingredients[1:]:
				out += "             %s\n" % ingredient
		out += "Steps:\n"
		for step in self.steps:
			out += "%s\n" % step
		out += "\n\n"
		return out

recipes = []
with open("full_recipes2.jsonlines") as full_recipes:
	recipe = None
	for line in full_recipes:
		if line.startswith("{\"title\":"):
			title = line.split("\\r\\n\\t", 1)[1].split("\\r\\n", 1)[0].replace(" - Allrecipes.com", "")
			if title != "Recipes":
				recipe = Recipe(title)
		elif line == "{\"end_of_recipe\": \"END_OF_RECIPE\"}\n":
			if recipe is not None: recipes.append(recipe)
			recipe = None
		elif recipe is not None:
			if line.startswith("{\"ingredient\": [\""):
				ingredient = line.split("{\"ingredient\": [\"", 1)[1].split("\"]}")[0]
				recipe.addIngredient(ingredient)
			elif line.startswith("{\"step\": [\""):
				step = line.split("{\"step\": [\"", 1)[1].split("\"]}")[0]
				recipe.addStep(step)

# print len(recipes)
print "\n".join([substep if substep.endswith(".") else substep + "." for recipe in recipes for step in recipe.steps for substep in step.split(". ")])
