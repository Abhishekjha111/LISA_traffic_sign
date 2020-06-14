from PIL import Image, ImageDraw, ImageFont
import os
import argparse
import shutil

parser = argparse.ArgumentParser(description='Mark or crop each annotation.',
			epilog='This program will create a directory called \'annotations\' and save the output there. The directory will be created in the folder where the annotation file is located. If the directory exists already, that will be used, and any existing files will be overwritten.')
parser.add_argument('mode', choices=['copy', 'mark', 'blackout', 'crop'], type=str, help='Copy will copy the frames with no alterations, mark will mark the annotation with a red box, blackout will black out the annotation, and crop will only save the annotation as a small image.')
parser.add_argument('path', metavar='filename.csv', type=str, help='The path to the csv-file containing the annotations.')
parser.add_argument('-f', '--filter', metavar='acceptedTag', type=str, help='If given, only annotations with this tag will be processed.')
parser.add_argument('-c', '--category', metavar='category', type=str, help='If given, the file categories.txt will be loaded and only signs with a tag that belongs to the given category are processed. categories.txt should be formatted with one category on each line in the format categoryName: tag1[, tag2, ... tagN]. It must be placed in the working directory.')
parser.add_argument('-m', '--margin', metavar='5', type=int, default=0, help='Add a margin around the crop/box/blackout equivalent to a percentage of the annotation\'s width/height. Ignored if mode is copy.')

args = parser.parse_args()

if not os.path.isfile(args.path):
	print("The given annotation file does not exist.\nSee annotateVisually.py -h for more info.")
	exit()
	
if args.category != None and not os.path.isfile('categories.txt'):
	print("Error: A category was given, but categories.txt does not exist in the working directory.\nTo use this functionality, create the file with a line for each category in the format\ncategoryName: tag1[, tag2, ... tagN]")
	exit()

categories = {}
if args.category != None:
	categories = {k.split(':')[0] : [tag.strip() for tag in k.split(':')[1].split(',')] for k in open('categories.txt', 'r').readlines()}
	if args.category not in categories:
		print("Error: The category '%s' does not exist in categories.txt." % args.category)
		exit()

csv = open(os.path.abspath(args.path), 'r')
csv.readline() # Discard the header-line.
csv = csv.readlines()
csv.sort()

basePath = os.path.dirname(args.path)
savePath = os.path.join(basePath, 'annotations')
if not os.path.isdir(savePath):
	os.mkdir(savePath)

font = ImageFont.load_default()

im = Image.new('RGB', (1,1))
counter = 0
previousFile = ''
for line in csv:
	fields = line.split(";")
	
	if args.filter != None and args.filter != fields[1]:
		continue
		
	if args.category != None and fields[1] not in categories[args.category]:
		continue
	
	if args.mode == 'copy':
		shutil.copy(os.path.join(basePath, fields[0]), savePath)
		print(os.path.join(savePath, fields[0]))
		counter += 1
		continue
		
	width = int(fields[4])-int(fields[2]);
	height = int(fields[5])-int(fields[3]);
	box = [int(fields[2])-width*args.margin/100, int(fields[3])-height*args.margin/100, int(fields[4])+width*args.margin/100, int(fields[5])+height*args.margin/100]
	
	if fields[0] != previousFile and args.mode != 'crop': # Save the drawn annotations and open the next file (crop opens its own images).
		im = Image.open(os.path.join(basePath, fields[0]))
	
	draw = ImageDraw.Draw(im)
	if args.mode == 'blackout':
		draw.rectangle(box, outline=(0,0,0), fill=(0,0,0));
	elif args.mode == 'mark':
		draw.rectangle(box, outline=(255,0,0));
		
		textSize = font.getsize(fields[1])
		draw.rectangle([int(fields[2]), int(fields[3])-textSize[1]-4, int(fields[2])+textSize[0]+2, int(fields[3])-1], outline=(0,0,0), fill=(0,0,0));
		draw.text((int(fields[2])+2, int(fields[3])-textSize[1]-2), fields[1], font=font)
	elif args.mode == 'crop':
		im = Image.open(os.path.join(basePath, fields[0])) # When cropping, the full image should always be opened.
		im = im.crop(box)
	
	if args.mode == 'crop':
		filename = os.path.join(savePath, '%d_%s' % (counter, os.path.basename(fields[0])))
	else:
		filename = os.path.join(savePath, os.path.basename(fields[0]))
	im.save(filename)
	print(filename)
	
	previousFile = fields[0]
	counter += 1

print("Done. Processed %d annotations." % (counter+1))
