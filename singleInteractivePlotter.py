# from astropy import units as u
from matplotlib import pyplot as plt 
# from astropy.visualization import quantity_support
# quantity_support()
import sys
import os.path

#check for number of arguments
if (len(sys.argv) != 2) :
	sys.exit("Usage: python3 singleInteractivePlotter.py <filepath>")

#check that filepath is valid
filepath = sys.argv[1]
if (os.path.exists(filepath) is False) :
	sys.exit("Could not find file with path: " + filepath)
if (filepath.endswith(".txt") is False) :
	sys.exit("The provided file is not a .txt file: " + filepath)

ifile = open(filepath, 'r')

#variable declarations
frequency = 0.0
intensity = 0.0
frequencyList = []
intensityList = []
NaNcount = 0

#read 21 header lines before data appears
for i in range(0,21) :
	line = ifile.readline()
	#parse time
	if (i == 3) : 
		hours = float((line.split())[3])
		minutes = 60 * (hours % 1)
		seconds = 60 * (minutes % 1)
		displaytime = ("%02d:%02d:%02d" % (hours, minutes, seconds))


# parse data from text file
while (1) :
	#take in the data line by line
	line  = ifile.readline()
	data = line.split()

	#end of file condition (no more rows in table)
	length = len(data)
	if (length < 4) : break

	#extract frequency and intensity data to be plotted
	frequency = float(data[2])
	intensity = float(data[3])

	#store frequency and intensity pair
	#skip points with invalid intensity (NaN)
	if (data[3] == "NaN") :
		NaNcount += 1
		continue
	frequencyList.append(frequency)
	intensityList.append(intensity)

print(str(len(frequencyList)) + " valid data points read in")
print(str(NaNcount) + " points with invalid intensity ignored")

ifile.close()


#graphing and display
c = plt.figure(figsize=(10,6))
plt.plot(frequencyList,intensityList, color='red', linewidth=0.5)
plt.xlabel("Frequency (Ghz)")
plt.ylabel("Flux Density (Jy)")
plt.suptitle(displaytime)
plt.show()


