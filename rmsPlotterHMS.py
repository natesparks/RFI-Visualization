from matplotlib import pyplot as plt 
import sys
import os.path
import glob
from math import sqrt
import numpy as np
import datetime
import timestampHandler
from rfiTableHandler import rfiTableHandler
    
def calcRMSoverTime(source_directory, freq_min, freq_max) :
    # list of all filepaths within directory
    filepathlist = (glob.glob(source_directory + "/*.txt"))

    # go through each scan to get the time and rms for a given frequency range
    timeList = []
    rmsList = []
    for filepath in filepathlist :
        # variable declarations
        curr_rfiTableHandler = rfiTableHandler(filepath)
        rms = curr_rfiTableHandler.calcRMSsingleChannel(freq_min, freq_max)
        rmsList.append(rms)
        timeList.append(curr_rfiTableHandler.scanDatetime)
    # print(f"{freq_min} {freq_max} has rms list:")
    # print(rmsList)
    return (timeList, rmsList)


    
def plotRMS(timeList, rmsList, freq_min, freq_max, timestamp_filepath) :
    # start and end time for formatting purposes
    starttime = min(timeList)
    endtime = max(timeList)

    # format axes and text
    currentFigure = plt.figure(figsize=(10,6))
    plt.xlabel("Time (UTC Hours)")
    plt.ylabel("RMS (Jy)")
    title = f"RMS over time [{starttime.strftime('%H:%M:%S')}, {endtime.strftime('%H:%M:%S')}] in range [{freq_min}, {freq_max}] (GHz)"
    plt.suptitle(title)
    plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"
    plt.xlim(starttime, endtime) # Comment out to add padding         

    # plot rms
    plt.plot(timeList, rmsList, color='black', linewidth=1.0)

    # display events on graph, if any exist
    if (timestamp_filepath != "") :
        print("Reading: " + timestamp_filepath)
        # read timestamps
        eventnames, eventdatetimes = timestampHandler.parsefile(timestamp_filepath)
        # shade background sections corresponding to timestamps
        labellist = []
        eventColorMap = {'All_on' : 'silver', 'Xband_off' : 'turquoise', 'Kuband_off' : 'blue', 'Fat_fingering' : 'crimson'}
        lastEventTime = max(eventdatetimes)
        for i, data in enumerate(zip(eventnames, eventdatetimes)) :
            eventname, eventtime = data
            # label section if color not already labelled
            label = ""
            if (eventname not in labellist) :
                labellist.append(eventname)
                label = eventname
            # plot last event as fixed 5 minute band going past the last data point
            if (eventtime == lastEventTime) :
                plt.axvspan(eventtime, eventtime + datetime.timedelta(minutes=5), facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)
            else :
                plt.axvspan(eventtime, eventdatetimes[i+1], facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)
        plt.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
        
    plt.tight_layout() # prevent legend from getting cut off
    plt.show()


def main() :
    # check for number of arguments
    numargs = len(sys.argv)
    if (numargs < 4 or numargs > 5) :
        sys.exit("Usage: python3 rmsPlotterHMS.py <source_directory> <freq_min> <freq_max> [event_timestamps]")

    # check that source directory is valid
    source_directory = sys.argv[1]
    if (os.path.isdir(source_directory) is False) :
        sys.exit("Could not find source directory with name: " + source_directory)

    # check that timestamp filepath is valid
    if (numargs == 5) :
        timestamp_filepath = sys.argv[4]
        if (os.path.exists(timestamp_filepath) is False) :
            sys.exit("Could not find file with path: " + timestamp_filepath)
        if (timestamp_filepath.endswith(".txt") is False) :
            sys.exit("The provided file is not a .txt file: " + timestamp_filepath)
        event_timestamps = sys.argv[4]
    # no timestamp file provided
    else :
        event_timestamps=  ""

    # parse frequency range args
    freq_min = float(sys.argv[2])
    freq_max = float(sys.argv[3])


    timeList, rmsList = calcRMSoverTime(source_directory, freq_min, freq_max)
    plotRMS(timeList, rmsList, freq_min, freq_max, event_timestamps)


if __name__ == '__main__':
    main()



