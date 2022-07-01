import csv
import sys
import os.path
from matplotlib import pyplot as plt 
import matplotlib.dates as mdates
import datetime
import numpy as np 
import glob
import timestampHandler
from rfiTableHandler import rfiTableHandler

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
executionStart = datetime.datetime.now()
print("Preparing to read: " + telemetry_filepath)
with open(telemetry_filepath) as csvFile:
    csvReader = csv.reader(csvFile, delimiter = ',')

    #get column headers
    headers = next(csvReader)

    #data sets
    timeArray = []
    rx_channelArray = []
    satellite_idArray = []
    timeMatch = FieldColPair("timestamp (GMT+00:00 UTC)", 0)
    rxMatch = FieldColPair("rx_channel_id", 0)
    sat_idMatch = FieldColPair("satellite_id", 0)
    fieldColPairs = [timeMatch, rxMatch, sat_idMatch]
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

        #store data
        timeArray.append(satTime)
        rx_channelArray.append(rx_channel)
        satellite_idArray.append(satellite_id)

        linenum += 1
print(f"Read in {linenum} lines from {telemetry_filepath}")
executionEnd = datetime.datetime.now()
print(f"Telemetry exec time: {executionEnd - executionStart}")


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
ax1.scatter(hmsArray, list(map(int, rx_channelArray)), marker='o', color='black')


# Channel data
channelfreqArray = [('1', 10.70, 10.95), ('2', 10.95, 11.20), ('3', 11.20, 11.45), ('4', 11.45, 11.70), ('5', 11.70, 11.95), ('6', 11.95, 12.20), ('7', 12.20, 12.45), ('8', 12.45, 12.7)]
channelColorMap = {'1' : 'brown', '2' : 'black', '3' : 'crimson', '4' : 'orange', '5' : 'orangered', '6' : 'teal', '7' : 'cyan', '8' : 'blue'}
channelTimeLists = {channelNum : [] for (channelNum, freq_min, freq_max) in channelfreqArray}
channelrmsLists = {channelNum : [] for (channelNum, freq_min, freq_max) in channelfreqArray}

# Calculate rms for each channel for each scan file
executionStart = datetime.datetime.now()
numTotalScans = len(scanFilepathList)
numCompleteScans = 0
nextExecutionMilestone = 0 #percent 
for scanFilepath in scanFilepathList :
    if ((numCompleteScans/numTotalScans)*100 >= nextExecutionMilestone) :  # display the percent of scans processed to the user
        print(f"{nextExecutionMilestone} % of RFI scans processed with RMS calculations performed")
        nextExecutionMilestone += 10
    curr_rfiTableHandler = rfiTableHandler(scanFilepath)
    channelrmsMap = curr_rfiTableHandler.calcRMSmultiChannel(channelfreqArray)  # returns array of each channel and its rms for this scan
    scanDatetime = curr_rfiTableHandler.scanDatetime
    for item in channelrmsMap.items() :
        channelNum, rms = item
        channelTimeLists[channelNum].append(scanDatetime)
        channelrmsLists[channelNum].append(rms)
    numCompleteScans += 1


# Display rms calculation execution time
executionEnd = datetime.datetime.now()
print(f"100% of RFI scans processed with execution time {executionEnd - executionStart}")

# RMS plot formatting
ax2.set_xlabel("Time (UTC HMS)")
ax2.set_ylabel("RMS (Jy)")
# ax2.set_ylim(0.0, 1.0) #clamp outliers


#Plot rms over time
for channelData in channelfreqArray :
    channelNum, freq_min, freq_max = channelData
    ax2.plot(channelTimeLists[channelNum], channelrmsLists[channelNum], color=channelColorMap[channelNum], linewidth=1.0, label=f"Channel {channelNum}")

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
        label = ""
        if (eventname not in labellist) :
            labellist.append(eventname)
            label = eventname
        #plot last event as fixed 5 minute band going past the last data point
        if (eventtime == lastEventTime) :
            ax1.axvspan(eventtime, eventtime + datetime.timedelta(minutes=5), facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)
            ax2.axvspan(eventtime, eventtime + datetime.timedelta(minutes=5), facecolor = eventColorMap[eventname], alpha=0.5, zorder=-100)
        else :
            ax1.axvspan(eventtime, eventdatetimes[i+1], facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)
            ax2.axvspan(eventtime, eventdatetimes[i+1], facecolor = eventColorMap[eventname], alpha=0.5, zorder=-100)

ax1.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
ax2.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
plt.tight_layout() #prevent legend from getting cut off
plt.show()

