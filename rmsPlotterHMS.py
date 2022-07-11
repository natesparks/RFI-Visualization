from matplotlib import pyplot as plt 
import sys
import os.path
import glob
from math import sqrt
import numpy as np
import datetime
import timestampHandler
from rfiTableHandler import rfiTableHandler

    
def plotRMS(sourceDirectory, freq_min, freq_max, timestampFilepath="") :
    # check that source directory is valid
    sourceDirectory = sys.argv[1]
    if (os.path.isdir(sourceDirectory) is False) :
        sys.exit("Could not find source directory with name: " + sourceDirectory)

    # check that timestamp filepath is valid, if one exists
    if (timestampFilepath != "") :
        if (os.path.exists(timestampFilepath) is False) :
            sys.exit("Could not find file with path: " + timestampFilepath)
        if (timestampFilepath.endswith(".txt") is False) :
            sys.exit("The provided file is not a .txt file: " + timestampFilepath)

    # list of all filepaths within directory
    filepathlist = (glob.glob(sourceDirectory + "/*.txt"))

    # go through each scan to get the time and rms for a given frequency range
    timeList = []
    rmsList = []
    for filepath in filepathlist :
        # variable declarations
        curr_rfiTableHandler = rfiTableHandler(filepath)
        rms = curr_rfiTableHandler.calcRMSsingleChannel(freq_min, freq_max)
        rmsList.append(rms)
        timeList.append(curr_rfiTableHandler.scanDatetime)

    # start and end time for formatting purposes
    starttime = min(timeList)
    endtime = max(timeList)

    # graph formatting
    currentFigure = plt.figure(figsize=(16,5))
    plt.xlabel("Time (UTC Hours)")
    plt.ylabel("RMS (Jy)")
    title = f"RMS over time [{starttime.strftime('%H:%M:%S')}, {endtime.strftime('%H:%M:%S')}] in range [{freq_min}, {freq_max}] (GHz)"
    plt.suptitle(title)
    plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"
    plt.xlim(starttime, endtime) # Comment out to add padding         

    # shade background sections corresponding to timestamps, if any exist
    if (timestampFilepath != "") :
        # read timestamps
        print("Reading: " + timestampFilepath)
        eventnames, eventdatetimes = timestampHandler.parsefile(timestampFilepath)
        eventColorMap = {'All_on' : 'silver', 'Xband_off' : 'turquoise', 'Kuband_off' : 'blue', 'Fat_fingering' : 'crimson'}
        labellist = []
        lastEventTime = max(eventdatetimes)

        # plot each event and give it a label
        for i, (eventname, eventtime) in enumerate(zip(eventnames, eventdatetimes)) :
            label = ""
            if (eventname not in labellist) :
                labellist.append(eventname)
                label = eventname
            # plot last event as fixed 5 minute band going past the last data point
            if (eventtime == lastEventTime) :
                plt.axvspan(eventtime, eventtime + datetime.timedelta(minutes=5), facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)
            else :
                plt.axvspan(eventtime, eventdatetimes[i+1], facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)

        # legend
        plt.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
        
    # plot rms over time
    plt.plot(timeList, rmsList, color='black', linewidth=1.0)

    # display plot
    plt.tight_layout() # prevent legend from getting cut off    
    plt.show()



if __name__ == '__main__':
    # check for number of arguments
    numargs = len(sys.argv)
    if (numargs < 4 or numargs > 5) :
        sys.exit("Usage: python3 rmsPlotterHMS.py <sourceDirectory> <freq_min> <freq_max> [event_timestamps]")
        
    # check for timestamp file
    timestampFilepath = ""
    if (numargs == 5) :
        timestampFilepath = sys.argv[4]

    plotRMS(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), timestampFilepath)



