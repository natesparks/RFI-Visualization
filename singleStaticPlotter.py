from matplotlib import pyplot as plt 
import sys
import os.path
from rfiTableHandler import rfiTableHandler
import channelDataHandler

#check for number of arguments
if (len(sys.argv) != 3) :
	sys.exit("Usage: python3 singleStaticPlotter.py <filepath> <target_dir>")

#check that filepath is valid
filepath = sys.argv[1]
if (os.path.exists(filepath) is False) :
	sys.exit("Could not find file with path: " + filepath)
if (filepath.endswith(".txt") is False) :
	sys.exit("The provided file is not a .txt file: " + filepath)
targetDir = sys.argv[2]
if (os.path.isdir(targetDir) is False) :
	sys.exit("Could not find target directory with name: " + targetDir)

# get frequency and intensity from rfiTable
freq_readMin = 0.0
freq_readMax = 100.0
curr_rfiTableHandler = rfiTableHandler(filepath)
frequencyList, intensityList = curr_rfiTableHandler.getFreqIntensity(freq_readMin, freq_readMax)
scanDatetime = curr_rfiTableHandler.scanDatetime

# graph formatting
c = plt.figure(figsize=(10,6))
plt.plot(frequencyList,intensityList, color='black', linewidth=0.5)
plt.xlabel("Frequency (Ghz)")
plt.ylabel("Flux Density (Jy)")
plt.suptitle(scanDatetime)

# get channel data and shade graph regions if there are any points in that region
channeldataArray = channelDataHandler.parsefile('channelData.txt')
channelColorMap = {'1' : 'brown', '2' : 'black', '3' : 'crimson', '4' : 'orange', '5' : 'orangered', '6' : 'teal', '7' : 'cyan', '8' : 'blue'}
for channeldata in channeldataArray :
    channelNum, freq_min, freq_max, = channeldata
    if (any(freq > freq_min and freq < freq_max for freq in frequencyList)) :
        plt.axvspan(freq_min, freq_max, facecolor = channelColorMap[channelNum], alpha=0.5, label=f"Channel {channelNum}", zorder=-100)        



#get file number
numIndex = filepath.find("_s") + 2
filenum = filepath[numIndex:numIndex+4]

#save figure
plt.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
print("Saving scan" + filenum)
targetPath = targetDir + "/" + "scan" + filenum + ".png"
plt.savefig(targetPath, bbox_inches='tight') 
print("Saved scan" + filenum + " to " + targetPath)


