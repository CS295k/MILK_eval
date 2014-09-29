from glob import glob
from xml.dom.minidom import parse
from itertools import islice
from os.path import basename, join, dirname, abspath, exists
from os import makedirs
from collections import defaultdict
from sexpdata import loads, ExpectClosingBracket, Symbol
import subprocess

idCount = -1
def buildGraphModel(sexp, labels, connections):
	global idCount
	idCount += 1
	id = "Node" + str(idCount)
	if type(sexp) == list:
		label = sexp[0]._val
		children = sexp[1:]
		labels[id] = label
		for child in children:
			connections[id].append(buildGraphModel(child, labels, connections))
	else:
		if type(sexp) == Symbol:
			labels[id] = sexp._val
		else:
			labels[id] = sexp
	return id

def buildGraphString(labels, connections, command):
	output = "graph SyntaxGraph {\n"
	output += "\tlabel = \"%s\";\n" % command.replace("\"", "\\\"")
	for i in xrange(len(labels)): # to guarantee that the nodes are put out in order
		id = "Node" + str(i)
		label = labels[id].replace("\"", "\\\"") if type(labels[id]) == str else labels[id]
		output += "\t%s [label=\"%s\"];\n" % (id, label)
	output += "\n"
	connectionLines = buildConnectionsInCorrectOrder(connections, "Node0")
	for line in connectionLines:
		output += "\t%s -- %s;\n" % (line[0], line[1])
	output += "}"
	return output

def buildConnectionsInCorrectOrder(connections, id):
	lines = []
	for child in connections[id]:
		lines.append((id, child))
	for child in connections[id]:
		lines += buildConnectionsInCorrectOrder(connections, child)
	return lines

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
	parseCounter = 0
	while parseCounter < len(sentenceParses):
		strippedFilename = basename(file).replace(".txt", "")
		sentence = annotatedMap[strippedFilename][annotatedCounter][0]
		command = annotatedMap[strippedFilename][annotatedCounter][1]
		if sentence == prevSentence:
			parseToUse = prevParse
		else:
			parseToUse = sentenceParses[parseCounter]
			prevSentence = sentence
			prevParse = parseToUse
			parseCounter += 1
		parseMap[strippedFilename].append((sentence, command, parseToUse))
		annotatedCounter += 1

# create a DOT file for each sentence parse
for file in parseMap:
	lineCount = 0
	for trip in parseMap[file]:
		try:
			command = trip[1]
			parsedSentence = trip[2]
			sexp = loads(parsedSentence)
			labels = {}
			connections = defaultdict(list)
			buildGraphModel(sexp, labels, connections)
			graphString = buildGraphString(labels, connections, command)
			filename = join(join(join(dirname(abspath(__file__)), "syntax_trees"), "dot_files"), file + "_" + str(lineCount) + ".dot")
			if not exists(dirname(filename)):
				makedirs(dirname(filename))
			output = open(filename, "w")
			output.write(graphString)
			output.close()
			idCount = -1
			lineCount += 1
		except ExpectClosingBracket as e:
			pass
			# print "There seem to be too few parens."
		except IndexError as e:
			pass
			# print "There seems to be an extra paren."

# convert each DOT file into a PDF
for file in glob("syntax_trees/dot_files/*.dot"):
	outputFile = join(join(join(dirname(abspath(__file__)), "syntax_trees"), "pdfs"), basename(file).replace(".dot", ".pdf"))
	if not exists(dirname(outputFile)):
		makedirs(dirname(outputFile))
	subprocess.call(["dot", "-Tpdf", file, "-o", outputFile])