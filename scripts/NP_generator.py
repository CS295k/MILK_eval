import operator
import collections
import random
import click

data_file = "train_test_NP_list.txt"

command_list = []

def file_reader():
	f = open(data_file, 'r')
	for line in f:
		command_list.append(line.rstrip('\n').encode('utf-8'))
	f.close()


def gen_NP(command, input_NP, mod):
	outputs = collections.Counter()
	for i in range(0, len(command_list)):
		line = command_list[i].split(' # ')
		if int(line[0]) != mod:
			cur_command = line[1].split(': ')[0]
			if cur_command == command:
				cur_NPs = line[1].split(': ')[1].split(' -> ')
				cur_input = cur_NPs[0]
				if input_NP in cur_input:
					cur_output = cur_NPs[1]
					if cur_command == 'separate':
						all_outputs = cur_output.split('; ')
						for np in all_outputs:
							outputs[np] += 1
					else:
						outputs[cur_output] += 1
	print outputs.most_common()
	return outputs

def main():
	file_reader()
	command = click.prompt('Enter command', type=str)
	input_NP = click.prompt('Enter input NP', type=str)
	mod = click.prompt('Enter mod (0-9)', type=click.IntRange(0, 9))
	gen_NP(command, input_NP, mod)

if __name__ == '__main__':
	main()
