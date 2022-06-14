import csv
import sys
import os.path
import requests as req 

#check for number of arguments
if (len(sys.argv) != 2) :
	sys.exit("Usage: python3 csvReader.py <filepath>")

#check that filepath is valid
filepath = sys.argv[1]
if (os.path.exists(filepath) is False) :
	sys.exit("Could not find file with path: " + filepath)
if (filepath.endswith(".csv") is False) :
	sys.exit("The provided file is not a .csv file: " + filepath)

with open(filepath) as csvFile:
    csvReader = csv.reader(csvFile, delimiter = ',')

    #get column headers
    headers = next(csvReader)

    timeArray = []
    rx_channelArray = []
    tx_channelArray = []
    satellite_idArray = []

    linenum = 1

    #parse data lines
    for row in csvReader :
        if (linenum == 1) :
            date = row[0].split()[0]
        time = row[0].split()[1] #leave as strings
        rx_channel = row[4]  
        tx_channel = row[5]
        satellite_id = row[6]

        #store data
        timeArray.append(time)
        rx_channelArray.append(rx_channel)
        tx_channelArray.append(tx_channel)
        satellite_idArray.append(satellite_id)

        linenum += 1

print("Read in " + str(linenum) + " lines from " + filepath )


#connect to celestrak to get updated TLE information
response = req.get("https://celestrak.com/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
if (response.status_code == 200) :
    print("Successfully connected to https://celestrak.com/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
else :
	sys.exit("Error - failed to connect to https://celestrak.com/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")

#read in TLE data from celestrak
TLEarray = response.text.splitlines()
print("Reading TLE data from celestrak.com...")

#parse the TLE for each satellite_id and map each satellite_id to its TLE
TLE_map = {} 
uniqueIDcount = 0
for i in range(len(TLEarray)) :
    satName = TLEarray[i].strip() #remove whitespace
    if ("STARLINK-" not in satName) : #skip other data fields besides name
        continue

    TLE_sat_id = satName[9:] #extract numbers from STARLINK-XXXX
    if (TLE_sat_id in satellite_idArray) :
        TLE_map[TLE_sat_id] = TLEarray[i+1] + " \n" + TLEarray[i+2] #2 lines after the name are the TLE
        uniqueIDcount += 1
print("Acquired TLE for", uniqueIDcount, "unique satellite IDs out of", len(satellite_idArray), "total satellite IDs in telemetry file")

#iterate through each (time, satellite_id) pair and map lookup the TLE
for i in range(len(satellite_idArray)) :
    tleText = TLE_map[satellite_idArray[i]]
    time = timeArray[i]
    #use the TLE and time to calculate position 
    

