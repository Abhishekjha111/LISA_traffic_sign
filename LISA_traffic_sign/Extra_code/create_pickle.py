'''
Create raw data pickle file
data_raw is a dict having mapping as image_filename -> [{'class': class_int, 'box_coords': (x1, y1, x2, y2)}, {...}, ...]
'''
import numpy as np
import re
import os
import pickle
from PIL import Image

# Script variables
RESIZE_IMAGE = True  # resize the images and write to 'resized_images/'
GRAYSCALE = True  # convert image to grayscale? this option is only valid if RESIZE_IMAGE==True
TARGET_W, TARGET_H = 400, 260  # 1.74 is weighted avg ratio, but 1.65 aspect ratio is close enough (1.65 was for stop signs)

###########################
# Execute main script
###########################

# First define mapping from sign name string to integer label

sign_list = ['addedLane', 'curveRight', 'dip', 'intersection', 'laneEnds', 'merge', 'pedestrianCrossing', 'signalAhead', 'slow', 'stopAhead',
			'thruMergeLeft', 'thruMergeRight', 'turnLeft', 'turnRight','yieldAhead']
sign_map = {'addedLane': 1, 'curveRight': 2, 'dip': 3, 'intersection':4, 'laneEnds':5, 'merge':6, 'pedestrianCrossing':7, 'signalAhead':8, 'slow':9, 'stopAhead':10,
'thruMergeLeft':11, 'thruMergeRight':12, 'turnLeft':13, 'turnRight':14, 'yieldAhead':15}

# Create raw data dictionary
data_raw = {}

# create a list to feed all the information from mergedAnnotation file
merged_annotations = []
with open('mergedAnnotations.csv', 'r') as f:
	for line in f:
		line = line[:-1]  # strip trailing newline
		merged_annotations.append(line)

# Create pickle file to represent dataset information
image_files = os.listdir('annotations')
for image_file in image_files:
	# Find box coordinates for all signs in this image
	class_list = []
	box_coords_list = []
	for line in merged_annotations:
		if re.search(image_file, line):
			fields = line.split(';')

			# Get sign name and assign class label
			sign_name = fields[1]
			
			if sign_name not in sign_list:
				continue  # ignore signs that are not in the list
			sign_class = sign_map[sign_name]
			class_list.append(sign_class)

			# Resize image, get rescaled box coordinates
			box_coords = np.array([int(x) for x in fields[2:6]])

			if RESIZE_IMAGE:
				# Resize the images and write to 'resized_images/'
				image = Image.open('annotations/' + image_file)
				orig_w, orig_h = image.size

				if GRAYSCALE:
					image = image.convert('L')  # 8-bit grayscale
				image = image.resize((TARGET_W, TARGET_H), Image.LANCZOS)  # downsampling filter

				resized_dir = 'resized_images_%dx%d/' % (TARGET_W, TARGET_H)
				if not os.path.exists(resized_dir):
					os.makedirs(resized_dir)

				image.save(os.path.join(resized_dir, image_file))

				# Rescale box coordinates
				x_scale = TARGET_W / orig_w
				y_scale = TARGET_H / orig_h

				ulc_x, ulc_y, lrc_x, lrc_y = box_coords
				new_box_coords = (ulc_x * x_scale, ulc_y * y_scale, lrc_x * x_scale, lrc_y * y_scale)
				new_box_coords = [round(x) for x in new_box_coords]
				box_coords = np.array(new_box_coords)

			box_coords_list.append(box_coords)

	if len(class_list) == 0:
		continue  # ignore images with no signs-of-interest
	class_list = np.array(class_list)
	box_coords_list = np.array(box_coords_list)

	# Create the list of dicts
	the_list = []
	for i in range(len(box_coords_list)):
		d = {'class': class_list[i], 'box_coords': box_coords_list[i]}
		print (d)
		the_list.append(d)

	data_raw[image_file] = the_list

with open('data_raw_%dx%d.p' % (TARGET_W, TARGET_H), 'wb') as f:
	pickle.dump(data_raw, f)
