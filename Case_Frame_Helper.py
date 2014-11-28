def treeToSentence(tree):
	if type(tree) == tuple:
		return " ".join(treeToSentence(child) for child in tree[1:])
	else:
		return tree