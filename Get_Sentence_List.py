from lxml import etree

def getSentenceList(filename):
	with open(filename, "r") as f:
		tree = etree.XML(f.read())
	sentences = [command.text for command in tree.findall(".//originaltext")]
	return sentences