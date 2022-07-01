from matplotlib import pyplot as plt 
import sys
import os.path
from rfiTableHandler import rfiTableHandler

#check for number of arguments
if (len(sys.argv) != 2) :
	sys.exit("Usage: python3 singleInteractivePlotter.py <filepath>")

#check that filepath is valid
filepath = sys.argv[1]
if (os.path.exists(filepath) is False) :
	sys.exit("Could not find file with path: " + filepath)
if (filepath.endswith(".txt") is False) :
	sys.exit("The provided file is not a .txt file: " + filepath)

freq_min = 0.0
freq_max = 100.0
curr_rfiTableHandler = rfiTableHandler(filepath)
frequencyList, intensityList = curr_rfiTableHandler.getFreqIntensity(freq_min, freq_max)
scanDatetime = curr_rfiTableHandler.scanDatetime

#graphing and display
c = plt.figure(figsize=(10,6))
plt.plot(frequencyList,intensityList, color='red', linewidth=0.5)
plt.xlabel("Frequency (Ghz)")
plt.ylabel("Flux Density (Jy)")
plt.suptitle(scanDatetime)
plt.show()


