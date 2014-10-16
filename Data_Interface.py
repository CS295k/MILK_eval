from xml.dom.minidom import parse

def getParseCommandPairs(file):
	pairs = []
	dom = parse(file)
	for elt in dom.getElementsByTagName("line")
		pairs.append((elt.getElementsByTagName("parsed-text")[0].childNodes[0].data, elt.getElementsByTagName("annotation")[0].childNodes[0].data))
	return pairs