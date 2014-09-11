MILK_eval
=========

MILK_eval is an evaluator for Dan Tasse's MILK, the Minimal Instruction Language for the Kitchen, as defined in his paper [Sour Cream: Toward Semantic Processing of Recipes](https://www.cs.cmu.edu/~nasmith/papers/tasse+smith.tr08.pdf).

Assumptions made
----------------

* All actions should use an empty string or an empty arguments place (two commas next to each other), rather than leaving the argument out of the list altogether.
* Put should allow for ingredient sets as input (i.e. put({ing1, ing2, ing3}, t1)) to put multiple ingredients into a single tool.
