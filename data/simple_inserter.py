#!/usr/bin/python

import sys

simple_ings = {}

def getSimpleNames(filename):
	global simple_ings
	f = open(filename, 'r')
	for line in f:
		#print line
		split_line = line.rstrip('\n').split(' -> ')
		#print split_line
		if split_line[1] != 'None':
			simple_ings[split_line[0]] = split_line[1]
			#print simple_ings[split_line[0]]
	f.close()

def insertIntoRecipes(filename):
	infile = open(filename)
	outfile= open(filename+'_simple.txt', 'w')

	for line in infile:
		for src, target in simple_ings.iteritems():
			line = line.replace(src, target)
		outfile.write(line)
	infile.close()
	outfile.close()

	#f = open(filename, 'r+')
	#for line in f:
	#	split_line = line.split('"')
	#	for n,i in enumerate(split_line):
	#		if i in simple_ings:
	#			#print split_line
	#			split_line[n] = simple_ings[i]
	#			print split_line



if __name__ == '__main__':
	getSimpleNames('simple_ings2.txt')
	insertIntoRecipes(sys.argv[1])


