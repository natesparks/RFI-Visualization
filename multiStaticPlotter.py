from matplotlib import pyplot as plt 
import sys
import os.path
import glob
from rfiTableHandler import rfiTableHandler
import channelDataHandler

#check for number of arguments
numargs = len(sys.argv)
if (numargs < 4 or numargs > 6) :
    sys.exit("Usage: python3 multiStaticPlotter.py <source_directory> <target_directory> <ymax> [freq_min] [freq_max]")

#check that directories are valid
sourceDir = sys.argv[1]
if (os.path.isdir(sourceDir) is False) :
    sys.exit("Could not find source directory with name: " + sourceDir)
targetDir = sys.argv[2]
if (os.path.isdir(targetDir) is False) :
    sys.exit("Could not find target directory with name: " + targetDir)

#parse x y range args
ymax = float(sys.argv[3])
freq_readMin = 0.0
freq_readMax = 100.0
if (numargs >= 5) : freq_min = float(sys.argv[4])
if (numargs == 6) : freq_max = float(sys.argv[5])

#list of all filepaths within directory
filepathlist = (glob.glob(sourceDir + "/*.txt"))


for filepath in filepathlist :
    # get frequency and intensity from rfiTable
    curr_rfiTableHandler = rfiTableHandler(filepath)
    frequencyList, intensityList = curr_rfiTableHandler.getFreqIntensity(freq_readMin, freq_readMax)
    scanDatetime = curr_rfiTableHandler.scanDatetime

    # graph formatting
    currentFigure = plt.figure(figsize=(10,6))
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

    # plot with legend
    plt.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
    plt.plot(frequencyList,intensityList, color='black', linewidth=0.5)

    #set y limit
    plt.ylim(0, ymax)
    
    #get file number and intnum
    scannumIndex = filepath.find("_s") + 2
    scannum = filepath[scannumIndex:scannumIndex+4]
    intnumIndex = filepath.find("_i")
    intnum = ""
    if (intnumIndex != -1) :
        intnumIndex += 2
        intnum = filepath[intnumIndex:intnumIndex+3]

    #save figure
    targetPath = targetDir + "/" + "scan" + scannum + "intnum" + intnum + ".png"
    print(f"Saving scan {targetPath}")
    plt.savefig(targetPath, bbox_inches='tight') 
    plt.close(currentFigure)

print("All static plots saved to directory: " + targetDir)
