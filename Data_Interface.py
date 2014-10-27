from glob import glob
from xml.dom.minidom import parse
from os.path import basename

def getParseCommandPairMappings():
	'''
	Returns a dictionary mapping from filename to list of parse-command pairs
	'''
	fileMappings = {}
	for filename in glob("parsed_annotated_recipes/*.xml"):
		pairs = []
		dom = parse(filename)
		for elt in dom.getElementsByTagName("line"):
			pairs.append((elt.getElementsByTagName("parsed-text")[0].childNodes[0].data, elt.getElementsByTagName("annotation")[0].childNodes[0].data))
		fileMappings[basename(filename)[:-4]] = pairs
	return fileMappings