#!/usr/bin/python

simple_ings = {}

def getSimpleNames():
	global simple_ings
	f = open('simple_ingredients0.txt', 'r')
	for line in f:
		print line
		split_line = line.split(' -> ')
		print split_line

if __name__ == '__main__':
	getSimpleNames()

