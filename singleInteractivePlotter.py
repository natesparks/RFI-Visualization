from matplotlib import pyplot as plt 
import sys
import os.path
from rfiTableHandler import rfiTableHandler
import channelDataHandler


def plotSingleInteractive(filepath) :
    # check that filepath is valid
    if (os.path.exists(filepath) is False) :
        sys.exit("Could not find file with path: " + filepath)
    if (filepath.endswith(".txt") is False) :
        sys.exit("The provided file is not a .txt file: " + filepath)

    # get frequency and intensity from rfiTable
    freq_readMin = 0.0
    freq_readMax = 100.0
    curr_rfiTableHandler = rfiTableHandler(filepath)
    frequencyList, intensityList = curr_rfiTableHandler.getFreqIntensity(freq_readMin, freq_readMax)
    scanDatetime = curr_rfiTableHandler.scanDatetime

    # graph formatting
    c = plt.figure(figsize=(10,6))
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
    plt.tight_layout() #prevent legend from getting cut off
    plt.plot(frequencyList,intensityList, color='black', linewidth=0.5)

    # display plot
    plt.show()


if __name__ == '__main__' :
    # check for number of arguments
    if (len(sys.argv) != 2) :
        sys.exit("Usage: python3 singleInteractivePlotter.py <filepath>")
    plotSingleInteractive(sys.argv[1])