import csv
import sys
import os.path
from matplotlib import pyplot as plt 
import datetime
import numpy as np 
import glob
from time import perf_counter
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import timestampHandler
from rfiTableHandler import rfiTableHandler
import channelDataHandler
import telemetryCsvHandler


def plotRxTelemetry(telemetryFilepath, scanDirectory, timestampFilepath) :
    #check that csv telemetry filepath is valid
    if (os.path.exists(telemetryFilepath) is False) :
        sys.exit("Could not find file with path: " + telemetryFilepath)
    if (telemetryFilepath.endswith(".csv") is False) :
        sys.exit("The provided file is not a .csv file: " + telemetryFilepath)

    # check that scan directory is valid
    if (os.path.isdir(scanDirectory) is False) :
        sys.exit("Could not find scan directory with name: " + scanDirectory)
    scanFilepathList = (glob.glob(scanDirectory + "/*.txt"))

    # check that timestamps filepath is valid
    if (timestampFilepath != "") :
        if (os.path.exists(timestampFilepath) is False) :
            sys.exit("Could not find file with path: " + timestampFilepath)
        if (timestampFilepath.endswith(".txt") is False) :
            sys.exit("The provided file is not a .txt file: " + timestampFilepath)
        
    # parse csv file
    executionStart = perf_counter()
    print("Preparing to read: " + telemetryFilepath)
    fieldList = ["timestamp (GMT+00:00 UTC)", "rx_channel_id", "satellite_id", "theta_offset"]
    linecount, dataListMap = telemetryCsvHandler.parsefile(telemetryFilepath, fieldList)

    # get data lists from csv parse output
    timeArray = dataListMap["timestamp (GMT+00:00 UTC)"]
    rx_channelArray = dataListMap["rx_channel_id"]
    satellite_idArray = dataListMap["satellite_id"]
    theta_offsetArray = dataListMap["theta_offset"]

    # display parsing stats
    executionEnd = perf_counter()
    print(f"Read in {linecount} lines from {telemetryFilepath} in {executionEnd - executionStart} sec")

    # format rx axes and text
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
    starttime = min(timeArray)
    endtime = max(timeArray)
    title = f"Downlink Channel Activity and GBT RMS from {starttime} to {endtime}"
    fig.suptitle(title)
    plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"
    # plt.xlim(starttime, endtime) #comment out to add padding 
    fig.set_size_inches(16, 9)

    # rx channel plot
    ax1.set_ylabel("rx_channel")
    executionStart = perf_counter()
    legend_elements = []

    # # plot without transparency
    # ax1.scatter(timeArray,list(map(int, rx_channelArray)), marker='o', color='black')

    # rx channel plot with transparency
    maxOffset = 60
    for offsetDiv in range(10, maxOffset, 10) :  # 6 divisions from 0 to 60
        lowerbound = offsetDiv - 10
        alpha = 1.1 - offsetDiv / maxOffset
        filtered_timeArray, filtered_rx_channelArray, filtered_theta_offsetArray = list(zip(*list(filter(lambda pair : pair[2] < offsetDiv and pair[2] >= lowerbound, zip(timeArray, list(map(int, rx_channelArray)), list(map(float, theta_offsetArray)))))))
        ax1.scatter(filtered_timeArray, filtered_rx_channelArray, marker='o', color='black', alpha=alpha)
        legend_elements.append(Line2D([0], [0], marker='o', color='white', markerfacecolor='black', alpha=alpha, label=f"{lowerbound}-{offsetDiv} deg"))
    executionEnd = perf_counter()
    print(f"Plotted telemetry points in {executionEnd - executionStart} sec")


    # channel data
    channeldataArray = channelDataHandler.parsefile('channelData.txt')
    channelColorMap = {'1' : 'brown', '2' : 'black', '3' : 'crimson', '4' : 'orange', '5' : 'orangered', '6' : 'teal', '7' : 'cyan', '8' : 'blue'}
    channelTimeLists = {channelNum : [] for (channelNum, freq_min, freq_max) in channeldataArray}
    channelrmsLists = {channelNum : [] for (channelNum, freq_min, freq_max) in channeldataArray}

    # calculate rms for each channel for each scan file
    executionStart = perf_counter()
    numTotalScans = len(scanFilepathList)
    numCompleteScans = 0
    nextExecutionMilestone = 0 #percent 
    for scanFilepath in scanFilepathList :
        if ((numCompleteScans/numTotalScans)*100 >= nextExecutionMilestone) :  # display the percent of scans processed to the user
            print(f"{nextExecutionMilestone} % of RFI scans processed with RMS calculations performed")
            nextExecutionMilestone += 10
        curr_rfiTableHandler = rfiTableHandler(scanFilepath)
        channelrmsMap = curr_rfiTableHandler.calcRMSmultiChannel(channeldataArray)  # returns array of each channel and its rms for this scan
        scanDatetime = curr_rfiTableHandler.scanDatetime
        for item in channelrmsMap.items() :
            channelNum, rms = item
            channelTimeLists[channelNum].append(scanDatetime)
            channelrmsLists[channelNum].append(rms)
        numCompleteScans += 1


    # display rms calculation execution time
    executionEnd = perf_counter()
    print(f"100% of RFI scans processed with execution time {executionEnd - executionStart} sec")

    # rms plot formatting
    ax2.set_xlabel("Time (UTC HMS)")
    ax2.set_ylabel("RMS (Jy)")
    # ax2.set_ylim(0.0, 1.0) #clamp outliers


    # plot rms over time
    for channelData in channeldataArray :
        channelNum, freq_min, freq_max = channelData
        ax2.plot(channelTimeLists[channelNum], channelrmsLists[channelNum], color=channelColorMap[channelNum], linewidth=1.0, label=f"Channel {channelNum}")

    # # Plot channel groups average rms over time
    # XbandTimeList = channelTimeLists['3']
    # XbandrmsList = np.array(channelrmsLists['4']) + np.array(channelrmsLists['5'])
    # KubandTimeList = channelTimeLists['6']
    # KubandrmsList = np.array(channelrmsLists['6']) + np.array(channelrmsLists['7']) + np.array(channelrmsLists['8'])
    # ax2.plot(KubandTimeList, KubandrmsList, color=channelColorMap['6'], linewidth=1.0, label=f"Channel 6, 7, 8")
    # ax2.plot(XbandTimeList, XbandrmsList, color=channelColorMap['3'], linewidth=1.0, label=f"Channel 4, 5")


    # check for an event timestamp file
    if (timestampFilepath != "") :
        print("Reading: " + timestampFilepath)
        
        eventnames, eventdatetimes = timestampHandler.parsefile(timestampFilepath)

        # Shade background sections corresponding to timestamps
        labellist = []
        eventColorMap = {'All_on' : 'silver', 'Xband_off' : 'turquoise', 'Kuband_off' : 'blue', 'Fat_fingering' : 'crimson'}
        lastEventTime = max(eventdatetimes)
        for i, data in enumerate(zip(eventnames, eventdatetimes)) :
            eventname, eventtime = data
            #label section if color not already labelled
            if (eventname not in labellist) :
                labellist.append(eventname)
                legend_elements.append(Line2D([0], [0], color=eventColorMap[eventname], alpha = 0.5, lw=6, label=eventname))
                
            #plot last event as fixed 5 minute band going past the last data point
            if (eventtime == lastEventTime) :
                ax1.axvspan(eventtime, eventtime + datetime.timedelta(minutes=5), facecolor = eventColorMap[eventname], alpha=0.5, zorder=-100)
                ax2.axvspan(eventtime, eventtime + datetime.timedelta(minutes=5), facecolor = eventColorMap[eventname], alpha=0.5, zorder=-100)
            else :
                ax1.axvspan(eventtime, eventdatetimes[i+1], facecolor = eventColorMap[eventname], alpha=0.5, zorder=-100)
                ax2.axvspan(eventtime, eventdatetimes[i+1], facecolor = eventColorMap[eventname], alpha=0.5, zorder=-100)

    # legends
    ax1.legend(handles=legend_elements, bbox_to_anchor = (1.0, 1.0), loc = 'upper left') 
    ax2.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')

    # display plot
    plt.tight_layout() #prevent legend from getting cut off
    plt.show()


if __name__ == '__main__' :
    #check for number of arguments
    numargs = len(sys.argv)
    if (numargs < 3 or numargs > 4) :
        sys.exit("Usage: python3 rxTelemetry.py <telemetryFilepath> <scanDirectory> [event_timestamps]")

    timestampFilepath = ""
    if (numargs == 4) :
        timestampFilepath = sys.argv[3]

    plotRxTelemetry(sys.argv[1], sys.argv[2], timestampFilepath)