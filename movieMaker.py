# import imageio as iio


# #check for number of arguments
# numargs = len(sys.argv)
# if (numargs != 4) :
# 	sys.exit("Usage: python3 animationProducer.py <source_directory> <target_directory> <target_filename>")

# #parse args and check that directories are valid
# sourceDir = sys.argv[1]
# if (os.path.isdir(sourceDir) is False) :
# 	sys.exit("Could not find source directory with name: " + sourceDir)
# targetDir = sys.argv[2]
# if (os.path.isdir(targetDir) is False) :
# 	sys.exit("Could not find target directory with name: " + targetDir)
# targetFilename = sys.argv[3]

# #get image paths from source directory
# sourcepathlist = (glob.glob(sourceDir + "/*.png"))

# #make image list
# imageList = [iio.imread(file) for file in sourcepathlist]


# #save gif
# targetPath = targetDir +  "/" + targetFilename + ".gif"
# print("Saving gif: " + targetPath)
# iio.mimwrite(targetPath, imageList)

import cv2
import numpy as np
import glob
import os.path
import sys

#check for number of arguments
numargs = len(sys.argv)
if (numargs != 4) :
	sys.exit("Usage: python3 movieMaker.py <source_directory> <target_directory> <target_filename>")

#parse args and check that directories are valid
sourceDir = sys.argv[1]
if (os.path.isdir(sourceDir) is False) :
	sys.exit("Could not find source directory with name: " + sourceDir)
targetDir = sys.argv[2]
if (os.path.isdir(targetDir) is False) :
	sys.exit("Could not find target directory with name: " + targetDir)


#target path
targetFilename = sys.argv[3]
targetPath = targetDir +  "/" + targetFilename + ".mp4"

#get image paths from source directory
sourcepathlist = (glob.glob(sourceDir + "/*.png"))

#check if any images exist
if (len(sourcepathlist) == 0 ) :
	sys.exit("Source directory has no .png files")

#determine movie parameters
height, width, layers = cv2.imread(sourcepathlist[0]).shape
size = (width, height)
fps = 5
fourcc = cv2.VideoWriter_fourcc(*'XVID')
vWriter = cv2.VideoWriter(targetPath, fourcc, fps, size)


#convert each filepath to an image object, then add to movie
for file in sourcepathlist :
	img = cv2.imread(file)
	vWriter.write(img)

#save movie
print("Saving movie to " + targetPath)
vWriter.release()





