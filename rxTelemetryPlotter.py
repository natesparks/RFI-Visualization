import csv
from re import X
import sys
import os.path
from matplotlib import pyplot as plt 
import matplotlib.dates as mdates
import datetime
import numpy as np 
import glob
from time import perf_counter
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import timestampHandler
from rfiTableHandler import rfiTableHandler
import channelDataHandler

class FieldColPair :
    def __init__(self, field, colnum) :
        self.field = field
        self.colnum = colnum

#check for number of arguments
numargs = len(sys.argv)
if (numargs < 3 or numargs > 4) :
    sys.exit("Usage: python3 rxTelemetry.py <telemetry_filepath> <scan_directory> [event_timestamps]")

#check that csv telemetry_filepath is valid
telemetry_filepath = sys.argv[1]
if (os.path.exists(telemetry_filepath) is False) :
    sys.exit("Could not find file with path: " + telemetry_filepath)
if (telemetry_filepath.endswith(".csv") is False) :
    sys.exit("The provided file is not a .csv file: " + telemetry_filepath)

# check that scan directory is valid
scan_directory = sys.argv[2]
if (os.path.isdir(scan_directory) is False) :
    sys.exit("Could not find scan directory with name: " + scan_directory)
scanFilepathList = (glob.glob(scan_directory + "/*.txt"))


#check that timestamps filepath is valid
if (numargs == 4) :
    timestamp_filepath = sys.argv[3]
    if (os.path.exists(timestamp_filepath) is False) :
        sys.exit("Could not find file with path: " + timestamp_filepath)
    if (timestamp_filepath.endswith(".txt") is False) :
        sys.exit("The provided file is not a .txt file: " + timestamp_filepath)
    

#start reading csv file
executionStart = perf_counter()
print("Preparing to read: " + telemetry_filepath)
with open(telemetry_filepath) as csvFile:
    csvReader = csv.reader(csvFile, delimiter = ',')

    #get column headers
    headers = next(csvReader)

    #data sets
    timeArray = []
    rx_channelArray = []
    satellite_idArray = []
    theta_offsetArray = []
    timeMatch = FieldColPair("timestamp (GMT+00:00 UTC)", 0)
    rxMatch = FieldColPair("rx_channel_id", 0)
    sat_idMatch = FieldColPair("satellite_id", 0)
    theta_offsetMatch = FieldColPair("theta_offset", 0)
    fieldColPairs = [timeMatch, rxMatch, sat_idMatch, theta_offsetMatch]

    #attempt to match data fields to column headers
    for columnNum in range(len(headers)) :
        for Pair in fieldColPairs :
            if (Pair.field in headers[columnNum]) :
                Pair.colnum = columnNum

    #display the matches
    print("Confirm the following data fields:")
    for Pair in fieldColPairs :
        print("Matched column <" + headers[Pair.colnum] + "> to field: <" + Pair.field + ">")

    #prompt user to manually change matches
    answer = input("Are the above fields correct? y/n ")
    if (answer == "n") :
        print("Update fields with the following format: update <field> <zero-indexed column number>")
        print("Range of valid column numbers is 0 to", len(headers)-1)
        print("Enter 'done' command when all fields are updated.")
        while (1) :
            answer = input()
            if (answer == "done") : break 
            command = answer.split()  
            if (len(command) == 3 and command[0] == "update" and (int(command[2]) in range(len(headers)))) : 
                print("command valid")
                for Pair in fieldColPairs :
                    if (Pair.field == command[1]) :
                        Pair.colnum = int(command[2]) #update colnum of Pair corresponding to entered field
            else :
                print("command invalid")
    #display new matches
    for Pair in fieldColPairs :
        print("Reading in column <" + headers[Pair.colnum] + "> for field: <" + Pair.field + ">")

    #parse data lines
    linenum = 1
    for row in csvReader :
        if (linenum == 1) :
            satDate = row[0].split()[0]
            satYear = int(satDate.split("/")[2])
            satMonth = int(satDate.split("/")[0])
            satDay = int(satDate.split("/")[1])
        satTime = row[timeMatch.colnum].split()[1] 

        rx_channel = row[rxMatch.colnum]  #leave as strings
        satellite_id = row[sat_idMatch.colnum]
        theta_offset = row[theta_offsetMatch.colnum].split()[0] #get rid of deg string

        #store data
        timeArray.append(satTime)
        rx_channelArray.append(rx_channel)
        satellite_idArray.append(satellite_id)
        theta_offsetArray.append(theta_offset)

        linenum += 1
executionEnd = perf_counter()
print(f"Read in {linenum} lines from {telemetry_filepath} in {executionEnd - executionStart} sec")


#determine datetime for each data point
hmsArray = []
for i, satTime in enumerate(timeArray) :
        satHour = int(satTime.split(":")[0])  #UTC time
        satMinute = int(satTime.split(":")[1])
        satSecond = 15 * (i % 4) #15 second intervals
        dt = datetime.datetime(satYear, satMonth, satDay, satHour, satMinute, satSecond) #time of day
        hms = dt
        hmsArray.append(hms)
starttime = min(timeArray)
endtime = max(timeArray)

#Format RX axes and text
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
title = f"Downlink Channel Activity and GBT RMS from {starttime} to {endtime}"
fig.suptitle(title)
plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"
# plt.xlim(starttime, endtime) #comment out to add padding 
fig.set_size_inches(16, 9)

# RX channel plot
ax1.set_ylabel("rx_channel")
executionStart = perf_counter()
legend_elements = []
# ax1.scatter(hmsArray,list(map(int, rx_channelArray)), marker='o', color='black') # plot without transparency

# RX channel plot with transparency
maxOffset = 60
for offsetDiv in range(10, maxOffset, 10) :  # 6 divisions from 0 to 60
    lowerbound = offsetDiv - 10
    alpha = 1.1 - offsetDiv / maxOffset
    filtered_hmsArray, filtered_rx_channelArray, filtered_theta_offsetArray = list(zip(*list(filter(lambda pair : pair[2] < offsetDiv and pair[2] >= lowerbound, zip(hmsArray, list(map(int, rx_channelArray)), list(map(float, theta_offsetArray)))))))
    ax1.scatter(filtered_hmsArray, filtered_rx_channelArray, marker='o', color='black', alpha=alpha)
    legend_elements.append(Line2D([0], [0], marker='o', color='white', markerfacecolor='black', alpha=alpha, label=f"{lowerbound}-{offsetDiv} deg"))
executionEnd = perf_counter()
print(f"Plotted telemetry points in {executionEnd - executionStart} sec")


# Channel data
channeldataArray = channelDataHandler.parsefile('channelData.txt')
channelColorMap = {'1' : 'brown', '2' : 'black', '3' : 'crimson', '4' : 'orange', '5' : 'orangered', '6' : 'teal', '7' : 'cyan', '8' : 'blue'}
channelTimeLists = {channelNum : [] for (channelNum, freq_min, freq_max) in channeldataArray}
channelrmsLists = {channelNum : [] for (channelNum, freq_min, freq_max) in channeldataArray}

# Calculate rms for each channel for each scan file
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


# Display rms calculation execution time
executionEnd = perf_counter()
print(f"100% of RFI scans processed with execution time {executionEnd - executionStart} sec")

# RMS plot formatting
ax2.set_xlabel("Time (UTC HMS)")
ax2.set_ylabel("RMS (Jy)")
# ax2.set_ylim(0.0, 1.0) #clamp outliers


# Plot rms over time
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


# Check for an event timestamp file
if (numargs == 4) :
    print("Reading: " + timestamp_filepath)
    
    eventnames, eventdatetimes = timestampHandler.parsefile(timestamp_filepath)

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

ax1.legend(handles=legend_elements, bbox_to_anchor = (1.0, 1.0), loc = 'upper left') 
ax2.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
plt.tight_layout() #prevent legend from getting cut off
plt.show()

