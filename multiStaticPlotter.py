from matplotlib import pyplot as plt 
import sys
import os.path
import glob
from rfiTableHandler import rfiTableHandler

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
freq_min = 0.0
freq_max = 100.0
if (numargs >= 5) : freq_min = float(sys.argv[4])
if (numargs == 6) : freq_max = float(sys.argv[5])

#list of all filepaths within directory
filepathlist = (glob.glob(sourceDir + "/*.txt"))


for filepath in filepathlist :
    curr_rfiTableHandler = rfiTableHandler(filepath)
    frequencyList, intensityList = curr_rfiTableHandler.getFreqIntensity(freq_min, freq_max)
    scanDatetime = curr_rfiTableHandler.scanDatetime

    #graphing
    currentFigure = plt.figure(figsize=(10,6))

    plt.xlabel("Frequency (Ghz)")
    plt.ylabel("Flux Density (Jy)")
    plt.suptitle(scanDatetime)
    plt.plot(frequencyList,intensityList, color='red', linewidth=0.5)

    #set y limit
    plt.ylim(0, ymax)
    
    #get file number
    scannumIndex = filepath.find("_s") + 2
    scannum = filepath[scannumIndex:scannumIndex+4]

    #get intnum, if exits
    intnumIndex = filepath.find("_i")
    intnum = ""
    if (intnumIndex != -1) :
        intnumIndex += 2
        intnum = filepath[intnumIndex:intnumIndex+3]
        

    #save figure
    targetPath = targetDir + "/" + "scan" + scannum + "intnum" + intnum + ".png"
    print(f"Saving scan {targetPath}")
    plt.savefig(targetPath) 
    # plt.show()
    plt.close(currentFigure)
    #plt.close('all')

#
print("All static plots saved to directory: " + targetDir)
