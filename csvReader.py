import csv
import sys
import os.path
import requests as req 

class FieldColPair :
    def __init__(self, field, colnum) :
        self.field = field
        self.colnum = colnum

#check for number of arguments
if (len(sys.argv) != 2) :
	sys.exit("Usage: python3 csvReader.py <filepath>")

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
    tx_channelArray = []
    satellite_idArray = []
    timeMatch = FieldColPair("timestamp (GMT+00:00 UTC)", 0)
    rxMatch = FieldColPair("rx_channel_id", 0)
    txMatch = FieldColPair("tx_channel_id", 0)
    sat_idMatch = FieldColPair("satellite_id", 0)
    fieldColPairs = [timeMatch, rxMatch, txMatch, sat_idMatch]
    #attempt to match data fields to column headers
    for columnNum in range(len(headers)) :
        for Pair in fieldColPairs :
            if (Pair.field in headers[columnNum]) :
                Pair.colnum = columnNum

    #display the matches
    print("Confirm the following data fields:")
    for Pair in fieldColPairs :
        print("Reading in column <" + headers[Pair.colnum] + "> for field: <" + Pair.field + ">")

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
            date = row[0].split()[0]
        time = row[timeMatch.colnum].split()[1] #leave as strings
        rx_channel = row[rxMatch.colnum]  
        tx_channel = row[txMatch.colnum]
        satellite_id = row[sat_idMatch.colnum]

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
TLEarray = response.text.splitlines() #raw text data
print("Reading TLE data from celestrak.com...")

#parse the TLE for each satellite_id and map each satellite_id to its TLE
TLE_map = {} 
uniqueIDcount = 0
for i in range(len(TLEarray)) :
    satName = TLEarray[i].strip() #remove whitespace
    if ("STARLINK-" not in satName) : #skip other data fields besides name
        continue

    id_num = satName[9:] #extract numbers from STARLINK-XXXX
    if (id_num in satellite_idArray) :
        TLE_map[id_num] = satName + '\n' + TLEarray[i+1] + " \n" + TLEarray[i+2] #two lines after the name are the two line element set
        uniqueIDcount += 1
print("Acquired TLE for", uniqueIDcount, "unique satellite IDs out of", len(satellite_idArray), "total satellite IDs in telemetry file")

#iterate through each (time, satellite_id) pair and map lookup the TLE
for i in range(len(satellite_idArray)) :
    tleText = TLE_map[satellite_idArray[i]]
    time = timeArray[i]
    #use the TLE and time to calculate position 
    

