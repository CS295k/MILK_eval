from glob import glob
from xml.dom.minidom import parse
from os.path import basename, join, dirname, abspath, exists
from os import makedirs
from sexpdata import loads, ExpectClosingBracket, Symbol
from collections import defaultdict
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

# create a DOT file for each sentence parse
for file in glob("parsed_annotated_recipes/*.xml"):
	try:
		dom = parse(file)
	except:
		print "The file %s had some parsing error." % file
	lineCount = 0
	for elt in dom.getElementsByTagName("line"):
		try:
			parsedSentence = elt.getElementsByTagName("parsed-text")[0].childNodes[0].data
			command = elt.getElementsByTagName("annotation")[0].childNodes[0].data
			sexp = loads(parsedSentence)
			labels = {}
			connections = defaultdict(list)
			buildGraphModel(sexp, labels, connections)
			graphString = buildGraphString(labels, connections, command)
			filename = join(join(join(dirname(abspath(__file__)), "syntax_trees"), "dot_files"), basename(file) + "_" + str(lineCount) + ".dot")
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
		except:
			pass
			# print "This is probably an Error indication in place of a real parse."

# convert each DOT file into a JPG
for file in glob("syntax_trees/dot_files/*.dot"):
	outputFile = join(join(join(dirname(abspath(__file__)), "syntax_trees"), "pdfs"), basename(file).replace(".dot", ".pdf"))
	if not exists(dirname(outputFile)):
		makedirs(dirname(outputFile))
	subprocess.call(["dot", "-Tpdf", file, "-o", outputFile])