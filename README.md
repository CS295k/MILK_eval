MILK_eval
=========

MILK_eval is an evaluator for Dan Tasse's MILK, the Minimal Instruction Language for the Kitchen, as defined in his paper [Sour Cream: Toward Semantic Processing of Recipes](https://www.cs.cmu.edu/~nasmith/papers/tasse+smith.tr08.pdf).

Assumptions made
----------------

* Ingredient location should be maintained when changes are made to the ingredient (i.e. if an ingredient is mixed, the output ingredient should be in the same container as the original ingredient)
* Cooking should automatically place the ingredient into the tool used if the tool is not null
* All actions should use an empty string or an empty arguments place (two commas next to each other), rather than leaving the argument out of the list altogether.
* Put should allow for ingredient sets as input (i.e. put({ing1, ing2, ing3}, t1)) to put multiple ingredients into a single tool.
