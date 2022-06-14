from astropy import units as u
from matplotlib import pyplot as plt 
from astropy.visualization import quantity_support
quantity_support()
import sys
import os.path
import glob

#check for number of arguments
numargs = len(sys.argv)
if (numargs < 4 or numargs > 6) :
	sys.exit("Usage: python3 multiStaticPlotter.py <source_directory> <target_directory> <ymax> [xmin] [xmax]")

#check that directories are valid
sourceDir = sys.argv[1]
if (os.path.isdir(sourceDir) is False) :
	sys.exit("Could not find source directory with name: " + sourceDir)
targetDir = sys.argv[2]
if (os.path.isdir(targetDir) is False) :
	sys.exit("Could not find target directory with name: " + targetDir)

#parse x y range args
ymax = float(sys.argv[3])
xmin = 0.0
xmax = 100.0
if (numargs >= 5) : xmin = float(sys.argv[4])
if (numargs == 6) : xmax = float(sys.argv[5])

#list of all filepaths within directory
filepathlist = (glob.glob(sourceDir + "/*.txt"))



for filepath in filepathlist :
	# variable declarations
	frequency = 0.0
	intensity = 0.0
	frequencyList = []
	intensityList = []
	NaNcount = 0

	ifile = open(filepath, 'r')

	#read 21 header lines before data appears
	for i in range(0,21) :
		line = ifile.readline()
		#parse time
		if (i == 3) : 
			hours = float((line.split())[3])
			minutes = 60 * (hours % 1)
			seconds = 60 * (minutes % 1)
			displaytime = ("%02d:%02d:%02d" % (hours, minutes, seconds))

	# parse data from file
	while (1) :
		#take in the data line by line
		line  = ifile.readline()
		data = line.split()

		#end of file condition
		length = len(data)
		if (length < 4) : break

		#extract data to be plotted
		frequency = float(data[2])
		intensity = float(data[3])

		#store frequency and intensity pair
		#skip points with invalid intensity (NaN)
		if (data[3] == "NaN") :
			NaNcount += 1
			continue
		#add data point if  frequency is in desired range [xmin,xmax]
		if (frequency >= xmin and frequency<=xmax) :
			frequencyList.append(frequency)
			intensityList.append(intensity)

	print(str(len(frequencyList)) + " valid data points read in")
	print(str(NaNcount) + " points with invalid intensity ignored")   # add scan number to output

	ifile.close()


	#graphing
	currentFigure = plt.figure(figsize=(10,6))

	plt.xlabel("Frequency (Ghz)")
	plt.ylabel("Flux Density (Jy)")
	plt.suptitle(displaytime)
	plt.plot(frequencyList,intensityList, color='red', linewidth=0.5)

	#set y limit
	plt.ylim(0, ymax)
	
	#get file number
	numIndex = filepath.find("_s") + 2
	filenum = filepath[numIndex:numIndex+4]

	#save figure
	print("Saving scan" + filenum)
	targetPath = targetDir + "/" + "scan" + filenum + ".png"
	plt.savefig(targetPath) 
	# plt.show()
	plt.close(currentFigure)
	#plt.close('all')

#
print("All static plots saved to directory: " + targetDir)
