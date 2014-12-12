import operator
import collections
import random
import click
import ingredient_names2

data_file = "train_test_NP_list.txt"
head_file = "simple_ingredients3.txt"

command_list = []
head_list = {}

def file_reader():
	f = open(data_file, 'r')
	for line in f:
		command_list.append(line.rstrip('\n').encode('utf-8'))
	f.close()

def head_reader():
	f = open(head_file, 'r')
	for line in f:
		split_line = line.decode('utf-8').rstrip('\n').split(' -> ')
		#print line
		head_list[split_line[0]] = split_line[1]


def normalize(x):
	total = sum(x.values(), 0.0)
	for key in x:
		x[key] /= total
	return x

#given a command, input noun phrase, and mod
def gen_NP(command, input_NP, mod, isFromCommandLine = False):
	outputs = collections.Counter()
	length_outputs = collections.Counter()
	for i in range(0, len(command_list)):
		line = command_list[i].split(' # ')
		if int(line[0]) != mod:
			cur_command = line[1].split(': ')[0]
			if cur_command == command:
				cur_NPs = line[1].split(': ')[1].split(' -> ')
				cur_input = cur_NPs[0]
				if cur_command == 'combine':
					all_combined = input_NP.split('*')
					#print cur_input
					#print len(cur_input.split(', ')), len(all_combined)
					if all(map(lambda x: x in cur_input, all_combined)):
						cur_output = cur_NPs[1]
						outputs[cur_output] += 1
					if len(cur_input.split(', ')) - 1 == len(all_combined):
						cur_output = cur_NPs[1]
						length_outputs[cur_output] += 1
				else:
					if input_NP in cur_input:
						cur_output = cur_NPs[1]
						outputs[cur_output] += 1
	if(command != "combine" and not outputs):
		outputs[input_NP] += 1
	if(command == 'create_ing' and input_NP in head_list):
		outputs[head_list[input_NP]] += 1
	if not outputs:
		outputs = length_outputs
	normalize(outputs)
	if isFromCommandLine:
		print outputs.most_common()
	return outputs.most_common()

def main():
	file_reader()
	head_reader()
	command = click.prompt('Enter command', type=str)
	input_NP = click.prompt('Enter input NP', type=str)
	mod = click.prompt('Enter mod (0-9)', type=click.IntRange(0, 9))
	gen_NP(command, input_NP, mod, True)

if __name__ == '__main__':
	main()
