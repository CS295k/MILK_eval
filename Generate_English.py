from Case_Frame_Helper import *

caseFrameProbabilities = probabilitiesFromFile("Case_Frame_Probabilities.txt")
topLevelProbabilities = probabilitiesFromFile("Top_Level_Probabilities.txt")

inputs = [(verbs, {"ing": "ing", "tool": "tool", "manner": "manner"}, caseFrameProbabilities, topLevelProbabilities) for verbs in [["mix", "cook"]]]
for input in inputs:
	print inputToEnglish(None, input[0], input[1], input[2], input[3])