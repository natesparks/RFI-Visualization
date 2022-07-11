import cv2
import numpy as np
import glob
import os.path
import sys


def makeMovie(sourceDirectory, targetDirectory, targetFilename) :
	# parse args and check that directories are valid
	if (os.path.isdir(sourceDirectory) is False) :
		sys.exit("Could not find source directory with name: " + sourceDirectory)
	targetDirectory = sys.argv[2]
	if (os.path.isdir(targetDirectory) is False) :
		sys.exit("Could not find target directory with name: " + targetDirectory)

	# target path
	targetPath = targetDirectory +  "/" + targetFilename + ".mp4"

	# get image paths from source directory
	sourcepathList = (glob.glob(sourceDirectory + "/*.png"))

	# map scan numbers to source filepaths
	scanFilepathMap = {}
	for file in sourcepathList :
		filename = file.split('/')[-1]  
		filenum = int(filename[4:8])  #assumes format scanXXXXintnum.png
		scanFilepathMap[filenum] = file

	# check if any images exist
	if (len(sourcepathList) == 0 ) :
		sys.exit("Source directory has no .png files")

	# movie parameters
	height, width, layers = cv2.imread(sourcepathList[0]).shape
	size = (width, height)
	fps = 5
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	vWriter = cv2.VideoWriter(targetPath, fourcc, fps, size)


	# convert each filepath to an image object, then add to movie
	for scannum, file in sorted(scanFilepathMap.items()) :
		img = cv2.imread(file)
		vWriter.write(img)

	# save movie
	print("Saving movie to " + targetPath)
	vWriter.release()



if __name__ == '__main__' :
	# check for number of arguments
	numargs = len(sys.argv)
	if (numargs != 4) :
		sys.exit("Usage: python3 movieMaker.py <source_directory> <target_directory> <target_filename>")
	makeMovie(sys.argv[1], sys.argv[2], sys.argv[3])

