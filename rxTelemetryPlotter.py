import csv
import sys
import os.path
from matplotlib import pyplot as plt 
import matplotlib.dates as mdates
import datetime
import numpy as np 

class FieldColPair :
    def __init__(self, field, colnum) :
        self.field = field
        self.colnum = colnum

#check for number of arguments
numargs = len(sys.argv)
if (numargs < 2 or numargs > 3) :
	sys.exit("Usage: python3 rxTelemetry.py <filepath> [event_timesatmps]")

#check that csv filepath is valid
filepath = sys.argv[1]
if (os.path.exists(filepath) is False) :
	sys.exit("Could not find file with path: " + filepath)
if (filepath.endswith(".csv") is False) :
	sys.exit("The provided file is not a .csv file: " + filepath)

#check that timestamps filepath is valid
if (numargs == 3) :
    timestamp_filepath = sys.argv[2]
    if (os.path.exists(timestamp_filepath) is False) :
        sys.exit("Could not find file with path: " + timestamp_filepath)
    if (timestamp_filepath.endswith(".txt") is False) :
        sys.exit("The provided file is not a .txt file: " + timestamp_filepath)
    

#start reading csv file
print("Preparing to read: " + filepath)
with open(filepath) as csvFile:
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
print(f"Read in {linenum} lines from {filepath}")


#PLOT RX OVER TIME

#determine xticks
starttime = min(timeArray)
endtime = max(timeArray)
# numDivisions = 12 #can change this
# stepsize = ( endtime - starttime ) / numDivisions
# tickpositions = np.arange(starttime, endtime + stepsize, stepsize) #positions from firsttime to lasttime, inclusive

#determine datetime for each data point
hmsArray = []
for i, satTime in enumerate(timeArray) :
        satHour = int(satTime.split(":")[0])  #UTC time
        satMinute = int(satTime.split(":")[1])
        satSecond = 15 * (i % 4) #15 second intervals
        dt = datetime.datetime(satYear, satMonth, satDay, satHour, satMinute, satSecond) #time of day
        # dt = datetime.time(satHour, satMinute, satSecond) #time of day
        # hms = dt.strftime("%H %M %S)")
        hms = dt
        hmsArray.append(hms)


#format and plot axes and text
currentFigure = plt.figure(figsize=(10,6))
plt.xlabel("Time (UTC HMS)")
plt.ylabel("rx_channel")
title = f"Downlink channels from {starttime} to {endtime}"
plt.suptitle(title)
plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"

# plt.xlim(starttime, endtime) #comment out to add padding 


#plot data
plt.scatter(hmsArray, list(map(int, rx_channelArray)), marker='o', color='black')


#check for an event timestamp file
if (numargs == 3) :
    print("Reading: " + timestamp_filepath)
    eventnames =  []
    eventtimes = []
    #color cycle
    currentColor = 0

    #parse event timestamp data 
    with open(timestamp_filepath, 'r') as efile :
        header = efile.readline()
        while (1) :
            line = efile.readline()
            data = line.split()
            #end of file condition
            length = len(data)
            if (length != 2) : break

            #event name, time, and format
            eventname = data[0]
            eventnames.append(eventname)
            eventHour, eventMinute, eventSecond = tuple(map(int, data[1].split(':'))) #split into [h,m,s]
            eventtimes.append(datetime.datetime(satYear, satMonth , satDay, eventHour, eventMinute, eventSecond))

    #shade background sections corresponding to timestamps
    labellist = []
    eventColorMap = {'All_on' : 'silver', 'Xband_off' : 'turquoise', 'Kuband_off' : 'blue', 'Fat_fingering' : 'crimson'}
    lastEventTime = max(eventtimes)
    for i, data in enumerate(zip(eventnames, eventtimes)) :
        eventname, eventtime = data
        #label section if color not already labelled
        label = ""
        if (eventname not in labellist) :
            labellist.append(eventname)
            label = eventname
        #plot last event as fixed 5 minute band going past the last data point
        if (eventtime == lastEventTime) :
            plt.axvspan(eventtime, eventtime + datetime.timedelta(minutes=5), facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)
        else :
            plt.axvspan(eventtime, eventtimes[i+1], facecolor = eventColorMap[eventname], alpha=0.5, label = label, zorder=-100)

plt.legend(bbox_to_anchor = (1.0, 1.0), loc = 'upper left')
plt.tight_layout() #prevent legend from getting cut off
plt.show()

