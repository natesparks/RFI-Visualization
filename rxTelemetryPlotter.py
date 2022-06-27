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
if (len(sys.argv) != 2) :
	sys.exit("Usage: python3 rxTelemetry.py <filepath>")

#check that filepath is valid
filepath = sys.argv[1]
if (os.path.exists(filepath) is False) :
	sys.exit("Could not find file with path: " + filepath)
if (filepath.endswith(".csv") is False) :
	sys.exit("The provided file is not a .csv file: " + filepath)

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
            satYear = ("%04d" % int(satDate.split("/")[2]))
            satMonth = ("%02d" % int(satDate.split("/")[0]))
            satDay = ("%02d" % int(satDate.split("/")[1]))
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
minTime = min(timeArray)
maxTime = max(timeArray)
# numDivisions = 12 #can change this
# stepsize = ( maxTime - minTime ) / numDivisions
# tickpositions = np.arange(minTime, maxTime + stepsize, stepsize) #positions from firsttime to lasttime, inclusive

#determine datetime for each data point
hmsArray = []
for i, satTime in enumerate(timeArray) :
        satHour = int(satTime.split(":")[0])  #UTC time
        satMinute = int(satTime.split(":")[1])
        satSecond = 15 * (i % 4) #15 second intervals
        dt = datetime.datetime(2022, 5, 15, satHour, satMinute, satSecond) #time of day
        # dt = datetime.time(satHour, satMinute, satSecond) #time of day
        # hms = dt.strftime("%H %M %S)")
        hms = dt
        hmsArray.append(hms)


#format and display plot
currentFigure = plt.figure(figsize=(10,6))
plt.xlabel("Time (UTC HMS)")
plt.ylabel("rx_channel")
title = f"Downlink channels from {minTime} to {maxTime}"
plt.suptitle(title)
plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"

# plt.xlim(minTime, maxTime) #comment out to add padding 

plt.scatter(hmsArray, list(map(int, rx_channelArray)), marker='o', color='green')
plt.show()

