from matplotlib import pyplot as plt 
import sys
import os.path
import glob
from math import sqrt
import numpy as np
from cycler import cycler
import datetime

#check for number of arguments
numargs = len(sys.argv)
if (numargs < 4 or numargs > 5) :
    sys.exit("Usage: python3 rmsPlotterHMS.py <source_directory> <freq_min> <freq_max> [event_timestamps]")

#check that directories are valid
sourceDir = sys.argv[1]
if (os.path.isdir(sourceDir) is False) :
    sys.exit("Could not find source directory with name: " + sourceDir)

#check that timestamps filepath is valid
if (numargs == 5) :
    timestamp_filepath = sys.argv[4]
    if (os.path.exists(timestamp_filepath) is False) :
        sys.exit("Could not find file with path: " + timestamp_filepath)
    if (timestamp_filepath.endswith(".txt") is False) :
        sys.exit("The provided file is not a .txt file: " + timestamp_filepath)
    

#parse frequency range args
freq_min = float(sys.argv[2])
freq_max = float(sys.argv[3])

#list of all filepaths within directory
filepathlist = (glob.glob(sourceDir + "/*.txt"))


#go through each scan to get the time (x) and rms (y) for a given frequency range
timeList = []
rmsList = []
for filepath in filepathlist :
    # variable declarations
    rms = 0.0
    frequency = 0.0
    intensity = 0.0
    intensityList = []
    NaNcount = 0

    with open(filepath, 'r') as ifile :

        #read 21 header lines before data appears
        for i in range(0,21) :
            line = ifile.readline()
            #parse date
            if (i == 2) :
                scanDate = line.split()[2].split('-')
                scanYear = int(scanDate[0])
                scanMonth = int(scanDate[1])
                scanDay = int(scanDate[2])
            #parse time
            if (i == 3) : 
                scanHour = float((line.split())[3])
                scanMinute = 60 * (scanHour % 1) 
                scanSecond = 60 * (scanMinute % 1) 
        scanDatetime = datetime.datetime(scanYear, scanMonth, scanDay, int(scanHour), int(scanMinute), int(scanSecond)) 

        #Parse frequency and intensity data from file
        while (1) :
            #Take in the data line by line
            line  = ifile.readline()
            data = line.split()

            #End of file condition
            length = len(data)
            if (length < 4) : break

            #Extract frequency and intensity to calculate rms
            frequency = float(data[2])
            intensity = float(data[3])

            #Skip points less than frequency min
            if (frequency < freq_min) : continue
            #Stop reading if frequency max is exceeded
            if (frequency > freq_max) : break
            #Skip points with invalid intensity (NaN)
            if (data[3] == "NaN") :
                NaNcount += 1
                continue
            #Add intensity to list 
            intensityList.append(intensity)

        print("Reading: " + filepath)


    #Calculate rms
    rms = np.square(intensityList).mean()
    rms = sqrt(rms)
    # print("rms: " + str(rms))
    # print("time: " + str(hours) + " = " + displaytime)
    #Add time rms pair
    timeList.append(scanDatetime)
    rmsList.append(rms)

#Start and end time formatting purposes
starttime = min(timeList)
endtime = max(timeList)

#Format axes and text
currentFigure = plt.figure(figsize=(10,6))
plt.xlabel("Time (UTC Hours)")
plt.ylabel("RMS (Jy)")
title = f"RMS over time [{starttime.strftime('%H:%M:%S')}, {endtime.strftime('%H:%M:%S')}] in range [{freq_min}, {freq_max}] (GHz)"
plt.suptitle(title)
plt.rcParams["date.autoformatter.minute"] = "%H:%M:%S"
plt.xlim(starttime, endtime) #comment out to add padding         

#Plot rms
plt.plot(timeList, rmsList, color='black', linewidth=1.0)

#check for an event timestamp file
if (numargs == 5) :
    timestamp_filepath = sys.argv[4]
    print("Reading: " + timestamp_filepath)
    eventnames =  []
    eventtimes = []

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
            eventtimes.append(datetime.datetime(scanYear, scanMonth , scanDay, eventHour, eventMinute, eventSecond))

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








