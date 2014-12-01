import re

#inputfile = 'p1p/xaf'
inputfile = 'all_parses.txt'

verb_dict = {}

line_count = 0
doc_count = 57848 #from personal research, check research folder
verb_count = 698173 #from previous run

with open( inputfile ) as file:
	for line in file:
		line_count += 1
		m = re.findall('\(vb [a-z]*', line.lower())
		if m != []:
			for match in m:
				fmatch = match.lower().split(' ')[1] #formatted match
				if fmatch in verb_dict:
					verb_dict[fmatch] += 1
				else:
					verb_dict[fmatch] = 1

total_sum = 0
for w in sorted(verb_dict, key=verb_dict.get, reverse=False):
	print  '%s\t%s\t%2f' % (w, verb_dict[w], float(verb_dict[w])/verb_count * 100)
	total_sum += verb_dict[w]

print 'total number of unique verbs: %s' % len(verb_dict)
print 'total number of verbs: %s' % total_sum
print 'total number of lines: %s' % line_count
print 'total number of recipes: %s' % doc_count
print 'average number of verbs per line: %s' % (float(total_sum)/line_count)
print 'average number of verbs per recipe: %s' % (float(total_sum)/doc_count)

