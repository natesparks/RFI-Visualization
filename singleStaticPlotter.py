from matplotlib import pyplot as plt 
import sys
import os.path
from rfiTableHandler import rfiTableHandler
import channelDataHandler

def plotSingleStatic(filepath, targetDirectory) :
    # check that filepath and source directory are valid
    if (os.path.exists(filepath) is False) :
        sys.exit("Could not find file with path: " + filepath)
    if (filepath.endswith(".txt") is False) :
        sys.exit("The provided file is not a .txt file: " + filepath)
    if (os.path.isdir(targetDirectory) is False) :
        sys.exit("Could not find target directory with name: " + targetDirectory)

    # get frequency and intensity from rfiTable
    curr_rfiTableHandler = rfiTableHandler(filepath)
    frequencyList, intensityList = curr_rfiTableHandler.getFreqIntensity()
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
	
    # get file number and intnum
    scannumIndex = filepath.find("_s") + 2
    scannum = filepath[scannumIndex:scannumIndex+4]
    intnumIndex = filepath.find("_i")
    intnum = ""
    if (intnumIndex != -1) :
        intnumIndex += 2
        intnum = filepath[intnumIndex:intnumIndex+3]

    # save figure
    targetPath = targetDirectory + "/" + "scan" + scannum + "intnum" + intnum + ".png"
    print(f"Saving scan {targetPath}")
    plt.savefig(targetPath, bbox_inches='tight') 
    plt.close(currentFigure)


if __name__ == '__main__' :
    #check for number of arguments
    if (len(sys.argv) != 3) :
        sys.exit("Usage: python3 singleStaticPlotter.py <filepath> <target_dir>")
    plotSingleStatic(sys.argv[1], sys.argv[2])
