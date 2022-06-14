from matplotlib import pyplot as plt 
import sys
import os.path
import glob
from math import sqrt
import numpy as np
from cycler import cycler

#check for number of arguments
numargs = len(sys.argv)
if (numargs < 4 or numargs > 5) :
	sys.exit("Usage: python3 rmsPlotterHMS.py <source_directory> <freq_min> <freq_max> [event_timestamps]")

#check that directories are valid
sourceDir = sys.argv[1]
if (os.path.isdir(sourceDir) is False) :
	sys.exit("Could not find source directory with name: " + sourceDir)


#parse frequency range args
freq_min = float(sys.argv[2])
freq_max = float(sys.argv[3])

#list of all filepaths within directory
filepathlist = (glob.glob(sourceDir + "/*.txt"))

timeList = []
rmsList = []

#go through each scan to get the time (x) and rms (y) for a given frequency range
for filepath in filepathlist :
	# variable declarations
	rms = 0.0
	frequency = 0.0
	intensity = 0.0
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

	# parse frequency and intensity data from file
	while (1) :
		#take in the data line by line
		line  = ifile.readline()
		data = line.split()

		#end of file condition
		length = len(data)
		if (length < 4) : break

		#extract frequency and intensity to calculate rms
		frequency = float(data[2])
		intensity = float(data[3])

		#skip points less than frequency min
		if (frequency < freq_min) : continue
		#stop reading if frequency max is exceeded
		if (frequency > freq_max) : break
		#skip points with invalid intensity (NaN)
		if (data[3] == "NaN") :
			NaNcount += 1
			continue
		#add intensity to list 
		intensityList.append(intensity)

	print("Reading: " + filepath)
	# print(str(len(intensityList)) + " valid data points read in")
	# print(str(NaNcount) + " points with invalid intensity ignored")   # add scan number to output

	ifile.close()

	#calculate rms
	rms = np.square(intensityList).mean()
	rms = sqrt(rms)
	# print("rms: " + str(rms))
	# print("time: " + str(hours) + " = " + displaytime)
	#add time rms pair
	timeList.append(hours)
	rmsList.append(rms)


#determine HMS ticks
firsttime = timeList[0]
lasttime = timeList[-1]
numDivisions = 10 #can change this
stepsize = ( lasttime - firsttime ) / numDivisions
tickpositions = np.arange(firsttime, lasttime + stepsize, stepsize) #positions from firsttime to lasttime, inclusive
tickdisplays = []
for hposition in tickpositions :
	mposition = 60 * (hposition % 1)
	sposition = 60 * (mposition % 1)
	displaytime = ("%02d:%02d:%02d" % (hposition, mposition, sposition))
	tickdisplays.append(displaytime)
	

#graph the rms calculated from each scan
currentFigure = plt.figure(figsize=(10,6))
plt.xlabel("Time (UTC Hours)")
plt.ylabel("RMS (Jy)")
title = "RMS over time in range [%f, %f] (GHz)" % (freq_min, freq_max)
plt.suptitle(title)

plt.xlim(firsttime, lasttime) #comment out to add padding 
plt.plot(timeList, rmsList, color='red', linewidth=0.5)
plt.xticks(tickpositions, tickdisplays)

#check for an event timestamp file
if (numargs == 5) :
	event_file = sys.argv[4]
	print("Reading: " + event_file)
	eventnames=  []
	eventtimes = []
	#color cycle
	colors = ['b', 'lime', 'c', 'indigo', 'darkgreen']
	currentColor = 0

	#parse event timestamp data 
	with open(event_file, 'r') as efile :
		header = efile.readline()
		while (1) :
			line = efile.readline()
			data = line.split()
			#end of file condition
			length = len(data)
			if (length != 2) : break

			eventname = data[0]
			eventnames.append(eventname)
			eventhms = data[1].split(':') #split into [h,m,s]
			eventdecimal = float(eventhms[0]) + float(eventhms[1])/60 + float(eventhms[2])/3600 #convert hms to decimal
			eventtimes.append(eventdecimal)
			#plot event lines
			plt.axvline(x = eventdecimal, linewidth = 1, color = colors[currentColor] , label = eventname)
			currentColor = (currentColor + 1) % 5

	plt.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper right')
	


plt.show()








