from glob import glob
import operator
import click


@click.command()
@click.option('--previous_ingredient', prompt='Enter previous ingredient',
				help='Enter the last used ingredient')


def ngram_counter(previous_ingredient):

	out_ings = {}

	f = open('output_ings.txt', 'r')
	for line in f:
		cleaned_line = line.decode('utf-8').encode('ascii', 'ignore')
		if previous_ingredient in cleaned_line.rstrip('\n').split(' -> ')[0]:
			out_ing = cleaned_line.rstrip('\n').split(' -> ')[1].split(' (')[0]
			if out_ing not in out_ings:
				out_ings[out_ing] = 1
			else:
				out_ings[out_ing] += 1
	f.close()

	click.echo(sorted(out_ings.items(), key=operator.itemgetter(1), reverse=True))



if __name__ == '__main__':
		ngram_counter()	

