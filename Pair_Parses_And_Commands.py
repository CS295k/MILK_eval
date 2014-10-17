from collections import defaultdict
from glob import glob
from xml.dom.minidom import parse
from os.path import basename, join, dirname, abspath, exists
from os import makedirs
from itertools import islice

def clean(s):
	return s.replace("&", "&amp;")

annotatedMap = defaultdict(list)
parseMap = defaultdict(list)

# get information on sentence-command pairings
annotatedFiles = glob("annotated_recipes/*.xml")
for file in annotatedFiles:
	dom = parse(file)
	for elt in dom.getElementsByTagName("line"):
		annotatedMap[basename(file).replace(".rcp_tagged.xml", "")].append((elt.getElementsByTagName("originaltext")[0].childNodes[0].data, elt.getElementsByTagName("annotation")[0].childNodes[0].data))

# associate each sentence-command pairing with a sentence parse
parsedFiles = glob("data/parsed_recipes/*.txt")
for file in parsedFiles:
	sentenceParses = []
	for sentenceParse in islice(open(file, "r"), 2, None, 102):
		sentenceParses.append(sentenceParse)
	prevSentence = None
	prevParse = None
	annotatedCounter = 0
	parseCounter = -1
	strippedFilename = basename(file).replace(".txt", "")
	while annotatedCounter < len(annotatedMap[strippedFilename]):
		sentence = annotatedMap[strippedFilename][annotatedCounter][0]
		command = annotatedMap[strippedFilename][annotatedCounter][1]
		if sentence == prevSentence:
			parseToUse = prevParse
		else:
			parseCounter += 1
			try:
				parseToUse = sentenceParses[parseCounter]
			except:
				parseToUse = "Error: repeat English sentences not next to each other, and represented as a single parse in Charniak's output."
				print "The file %s has some problems, most likely related to repeat English sentences which received only one parse." % file
			prevSentence = sentence
			prevParse = parseToUse
		parseMap[strippedFilename].append((parseToUse, command))
		annotatedCounter += 1

for shortFilename in parseMap:
	xmlString = "<recipe>\n"
	for parseCommandPair in parseMap[shortFilename]:
		xmlString += "<line><parsed-text>%s</parsed-text><annotation>%s</annotation></line>\n" % (clean(parseCommandPair[0].strip()).encode("utf-8"), clean(parseCommandPair[1]).encode("utf-8"))
	xmlString += "</recipe>"
	
	# write the XML to the file
	filename = join(join(dirname(abspath(__file__)), "parsed_annotated_recipes"), shortFilename + ".xml")
	if not exists(dirname(filename)):
		makedirs(dirname(filename))
	file = open(join("parsed_annotated_recipes", filename), "w")
	file.write(xmlString)