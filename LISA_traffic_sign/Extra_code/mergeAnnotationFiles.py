import fnmatch
import os
import argparse

parser = argparse.ArgumentParser(description='Merge several annotation files to one large.',
			epilog='This program will create a file containing annotations from all annotation files in any subdirectory matching the patterns. This is handy for generating a file with all annotations to use with the other annotation tools.')
parser.add_argument('mode', choices=['frame', 'video'], type=str, help='Determines whether the script will merge video annotation files or frame annotation files.')
parser.add_argument('outputName', metavar='mergedAnnotations.csv', type=str, help='The name of the output file.')
parser.add_argument('filters', metavar='someFolder/', type=str, nargs='*',
                   help='Folders that the processed annotations must come from. If none are given, all subfolders are used.')


args = parser.parse_args()

if args.mode == 'frame':
	inputName = 'frameAnnotations.csv'
else:
	inputName = '*_annotations.csv'

fileMatches = []
for root, dirnames, filenames in os.walk('.'):
  for filename in fnmatch.filter(filenames, inputName):
      fileMatches.append(os.path.join(root, filename))

matches = []
if len(args.filters) > 0:
	for filter in args.filters:
		matches += [x for x in fileMatches if filter in x]
else:
	matches = fileMatches

if len(matches) == 0:
	print("No annotation files found, exiting...\n")
	exit()

matches = [x.replace('./', '') for x in matches]

outfile = open(args.outputName, 'w')

infile = open(matches[0], 'r')
outfile.write(infile.readline());
infile.close()

for csvFile in matches:
	infile = open(csvFile, 'r')
	lines = infile.readlines()
	outfile.write(''.join(csvFile.rpartition('/')[0:2]) + ''.join(csvFile.rpartition('/')[0:2]).join(lines[1:]))
	infile.close()

outfile.close()
