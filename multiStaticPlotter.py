from matplotlib import pyplot as plt 
import sys
import os.path
import glob
from rfiTableHandler import rfiTableHandler
import channelDataHandler


def plotMultiStatic(sourceDirectory, targetDirectory, ymax, ) :
    # check that directories are valid
    if (os.path.isdir(sourceDirectory) is False) :
        sys.exit("Could not find source directory with name: " + sourceDirectory)
    if (os.path.isdir(targetDirectory) is False) :
        sys.exit("Could not find target directory with name: " + targetDirectory)

    # list of all filepaths within directory
    filepathList = (glob.glob(sourceDirectory + "/*.txt"))

    for filepath in filepathList :
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

        # set y limit
        plt.ylim(0, ymax)
        
        # get file number and intnum
        scannumIndex = filepath.find("_s") + 2
        scannum = filepath[scannumIndex:scannumIndex+4]
        intnumIndex = filepath.find("_i")
        intnum = ""
        if (intnumIndex != -1) :
            intnumIndex += 2
            intnum = filepath[intnumIndex:intnumIndex+3]

        # save figure
        if ('/' not in targetDirectory) : targetDirectory += '/'
        targetPath = targetDirectory + "scan" + scannum + "intnum" + intnum + ".png"
        print(f"Saving scan {targetPath}")
        plt.savefig(targetPath, bbox_inches='tight') 
        plt.close(currentFigure)
    print("All static plots saved to directory: " + targetDirectory)


if __name__ == '__main__' :
    # check for number of arguments
    numargs = len(sys.argv)
    if (numargs < 4 or numargs > 6) :
        sys.exit("Usage: python3 multiStaticPlotter.py <source_directory> <target_directory> <ymax>")
    plotMultiStatic(sys.argv[1], sys.argv[2], float(sys.argv[3]))