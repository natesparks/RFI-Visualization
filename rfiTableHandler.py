import datetime
from math import sqrt
import numpy as np

class rfiTableHandler :
    def __init__(self, filepath) :
        self.filepath = filepath

        # Table Format Properties
        self.__headerlength = 22
        self.__dateLinenum = 2
        self.__timeLinenum = 3


    # Returns rms for a single frequency range within the scan (can be paired with attribute scanDatetime to plot rms over time)
    def calcRMSsingleChannel(self, freq_min, freq_max) :
        intensityList = []
        with open(self.filepath, 'r') as ifile :

            # Read header lines before data appears
            for i in range(0,self.__headerlength) :
                line = ifile.readline()
                # parse date
                if (i == self.__dateLinenum) :
                    scanDate = line.split()[2].split('-')
                    scanYear = int(scanDate[0])
                    scanMonth = int(scanDate[1])
                    scanDay = int(scanDate[2])
                # parse time
                if (i == self.__timeLinenum) : 
                    scanHour = float((line.split())[3]) #decimal hour, float values
                    scanMinute = 60 * (scanHour % 1) 
                    scanSecond = 60 * (scanMinute % 1) 
                if ("Frequency" in line and "Intensity" in line) :
                    break
            self.scanDatetime = datetime.datetime(scanYear, scanMonth, scanDay, int(scanHour), int(scanMinute), int(scanSecond)) 

            # Parse intensity data that is within frequency range
            while (1) :
                line  = ifile.readline()
                data = line.split()
                # EOF condition
                if (len(data) < 4) : break #should be 4 columns wide
                # extract frequency and intensity
                frequency = float(data[2])
                intensity = float(data[3])
                if (frequency < freq_min) : continue  # skip points less than frequency min
                if (frequency > freq_max) : break  # stop reading scan if frequency max is exceeded
                if (data[3] == "NaN") :  # skip points with invalid intensity (NaN)
                    NaNcount += 1
                    continue
                # add valid intensity to list
                intensityList.append(intensity)

        # Check for empty intensityList (no frequencies in this scan are within [freq_min, freq_max])
        if (not intensityList) :  
            rms = float("nan")
        else :
            # Calculate rms
            rms = sqrt(np.square(intensityList).mean())
        return rms


    # returns rms for each channel frequency range within the scan (calculated in parallel)
    def calcRMSmultiChannel(self, channelfreqArray) :
        channelIntensityLists = {channelNum : [] for (channelNum, freq_min, freq_max) in channelfreqArray}
        isChannelPastRange = {channelNum : False for (channelNum, freq_min, freq_max) in channelfreqArray}  #array of bools, each indicating whether to keep checking if a frequency is in the range of the channel

        with open(self.filepath, 'r') as ifile :

            # Read header lines before data appears
            for i in range(0,self.__headerlength) :
                line = ifile.readline()
                # parse date
                if (i == self.__dateLinenum) :
                    scanDate = line.split()[2].split('-')
                    scanYear = int(scanDate[0])
                    scanMonth = int(scanDate[1])
                    scanDay = int(scanDate[2])
                # parse time
                if (i == self.__timeLinenum) : 
                    scanHour = float((line.split())[3]) #decimal hour, float values
                    scanMinute = 60 * (scanHour % 1) 
                    scanSecond = 60 * (scanMinute % 1) 
                if ("Frequency" in line and "Intensity" in line) :
                    break
            self.scanDatetime = datetime.datetime(scanYear, scanMonth, scanDay, int(scanHour), int(scanMinute), int(scanSecond)) 

            # Parse intensity data that is within frequency range
            while (1) :
                line  = ifile.readline()
                lineData = line.split()
                # EOF condition
                if (len(lineData) < 4) : break #should be 4 columns wide
                # extract frequency and intensity
                frequency = float(lineData[2])
                intensity = float(lineData[3])

                # Check if lineData needs to be processed at all
                if (all(isChannelPastRange.values())) : break  # can stop reading any more lines when frequency exceeds all ranges
                if (lineData[3] == "NaN") :  # skip points with invalid intensity (NaN)
                    continue

                # Check validity of frequency for each channel
                for channelData in channelfreqArray :
                    channelNum, freq_min, freq_max = channelData

                    if (isChannelPastRange[channelNum]) : continue  # skip channel if past range
                    if (frequency >= freq_max) :  # flag that can stop reading channel since frequency max is exceeded    
                        isChannelPastRange[channelNum] = True
                        continue
                    if (frequency > freq_min) :  # add the valid intensity to list, and ignore other channels since no frequency overlap
                        channelIntensityLists[channelNum].append(intensity)
                        break

        # Determine rms for each channel
        channelrmsMap = {channelNum : float('nan') for (channelNum, freq_min, freq_max) in channelfreqArray}
        for (channelNum, intensityList) in channelIntensityLists.items() :
            # Check for empty intensityList (no frequencies in this scan are within [freq_min, freq_max])
            if (not intensityList) :  
                rms = float("nan")
            else :
                # Calculate rms
                rms = sqrt(np.square(intensityList).mean())
            channelrmsMap[channelNum] = rms
        return channelrmsMap
    
    #