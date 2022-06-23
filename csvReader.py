import csv
import sys
import os.path
import requests as req 
import configparser
import time
import datetime
import numpy as np
from astropy.coordinates import EarthLocation
from astropy import time
from astropy import units as u
from pycraf import satellite

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
        satTime = row[timeMatch.colnum].split()[1] #leave as strings
        rx_channel = row[rxMatch.colnum]  
        tx_channel = row[txMatch.colnum]
        satellite_id = row[sat_idMatch.colnum]

        #store data
        timeArray.append(satTime)
        rx_channelArray.append(rx_channel)
        tx_channelArray.append(tx_channel)
        satellite_idArray.append(satellite_id)

        linenum += 1

print(f"Read in {linenum} lines from {filepath}")

#function to parse the raw TLEs for each satellite_id and map each satellite_id to its TLE
def TLEMapper(satellite_idArray, raw_TLEs, TLE_map, idMode) :
    uniqueIDcount = 0
    if (idMode == "sat_id") :
        for i in range(len(raw_TLEs)) :
            satName = raw_TLEs[i].strip() #remove whitespace
            if ("STARLINK-" not in satName) : #skip other data fields besides name
                continue

            # id_num = satName[9:] #extract numbers from STARLINK-XXXX
            id_num = satName[9:13] #extract numbers from STARLINK-XXXX
            if (id_num in satellite_idArray) :
                TLE_map[id_num] = satName + '\n' + raw_TLEs[i+1] + " \n" + raw_TLEs[i+2] #two lines after the name are the two line element set
                uniqueIDcount += 1
    elif (idMode == "NORAD") :
        for i, line in enumerate(raw_TLEs) :
            line = line.split() #split the line to access indiv elements (line num and NORAD)
            if (line[0] != "1") : continue #skip lines that don't contain NORAD id (aka not line 1)
            NORAD_id = line[1]
            if ("U" in NORAD_id) :
                NORAD_id = NORAD_id[:-1] #strip U from back of NORAD id

            id_num = NORAD_satid_map[NORAD_id] #get corresponding sat_id from NORAD id
            if (id_num in satellite_idArray and id_num not in TLE_map.keys()) :
                TLE_map[id_num] = "STARLINK-" + str(id_num) + '\n' + raw_TLEs[i] + " \n" + raw_TLEs[i+1] #two lines after the name are the two line element set
                uniqueIDcount += 1


    print("Acquired TLE for", uniqueIDcount, "unique satellite IDs out of", len(satellite_idArray), "total satellite IDs in telemetry file")

#QUERY TLE DATABASES AND MAP sat ids to corresponding TLEs

#CELESTRAK UNCLASSIFIED
unclassified_TLE_map = {} 
response = req.get("https://celestrak.com/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
if (response.status_code == 200) :
    print("Successfully connected to https://celestrak.com/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
else :
	sys.exit("Error - failed to connect to https://celestrak.com/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
#read in TLE data from celestrak
print("Reading unclassified TLE data from celestrak.com...")
TLEMapper(satellite_idArray, response.text.splitlines(), unclassified_TLE_map, "sat_id")

#CELESTRAK CLASSIFIED
classified_TLE_map = {} 
response = req.get("http://www.celestrak.com/NORAD/elements/supplemental/starlink.txt")
if (response.status_code == 200) :
    print("Successfully connected to http://www.celestrak.com/NORAD/elements/supplemental/starlink.txt")
else :
	sys.exit("Error - failed to connect to http://www.celestrak.com/NORAD/elements/supplemental/starlink.txt")
#read in TLE data from celestrak
print("Reading classified TLE data from celestrak.com...")
TLEMapper(satellite_idArray, response.text.splitlines(), classified_TLE_map, "sat_id")

#SPACE TRACK
spacetrack_TLE_map = {} 
#prompt user to decide whether to requery Space Track for the historical TLEs
answer = ""
while (answer != "y" and answer != "n") :
    answer = input("Requery Space Track for the historical TLEs? y/n ")
NORAD_satid_map = {}
#get NORAD_CAT_ID from unclassified celestrak data and map to sat_id
print("Pulling NORAD IDs from celestrak data...")
for sat_id in unclassified_TLE_map :
    TLE = unclassified_TLE_map[sat_id].split()
    NORAD_CAT_ID = TLE[2][:-1] 
    NORAD_satid_map[NORAD_CAT_ID] = sat_id
#use NORAD_CAT_IDs to query Space Track
if (answer == "y") :
    NORAD_string = ", ".join(NORAD_satid_map.keys())
    queryText = f"https://www.space-track.org/basicspacedata/query/class/tle_publish/PUBLISH_EPOCH/~~{satYear}-{satMonth}-{satDay}/NORAD_CAT_ID/{NORAD_string}/orderby/NORAD_CAT_ID asc/format/tle/emptyresult/show"

    #get credentials from space-track.ini    
    config = configparser.ConfigParser()
    config.read("./space-track.ini")
    configUsr = config.get("configuration", "username")
    configPwd = config.get("configuration", "password")
    siteCred = {"identity": configUsr, "password": configPwd}
    #attempt to connect to space-track.org
    with req.Session() as session :
        #send credentials over POST request
        response = session.post("https://www.space-track.org/ajaxauth/login", data=siteCred)
        #successful login 
        if (response.status_code == 200) :
            response = session.get(queryText)
            #successful GET
            if (response.status_code == 200) :
                print("Successfully connected to https://www.space-track.org")
                TLEMapper(satellite_idArray, response.text.splitlines(), spacetrack_TLE_map, "NORAD")
                #store query response from space-track
                print("Storing query response...")
                with open("Historical_TLEs.txt", "w") as ofile :
                    ofile.write(response.text)
            #failed GET
            else :
                print("Error - failed to get data from https://www.space-track.org. Substituting space-track TLEs from most recent query.")
            #read in TLE data from space-track
        #failed login
        else :
            print("Error - failed login attempt to https://www.space-track.org. Substituting space-track TLEs from most recent query.")
#use stored historical TLEs from last Space Track query
else :
    with open("Historical_TLEs.txt") as ifile :
        TLEMapper(satellite_idArray, ifile.read().splitlines(), spacetrack_TLE_map, "NORAD")
    

#Verify the completeness of each mapping
missedCount = 0
for i, sat_id in enumerate(satellite_idArray) :
    if sat_id not in unclassified_TLE_map : 
        print(f"{sat_id} not found in unclassified_TLE_map")
        missedCount += 1
    if sat_id not in classified_TLE_map : 
        print(f"{sat_id} not found in classified_TLE_map")
        missedCount += 1
    if sat_id not in spacetrack_TLE_map :
        print(f"{sat_id} not found in spacetrack_TLE_map")
        missedCount += 1
    
#Use pycraf satellite library to calculate satellite positions
# gbt location
gbt_location = EarthLocation.of_site('gbt')
print(f"gbt_location: {gbt_location}")

# create a SatelliteObserver instance
sat_obs = satellite.SatelliteObserver(gbt_location)


#iterate through each (time, satellite_id) pair and map lookup the TLE
with open("sat_positions.csv", "w") as ofile :
    csv_writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #headers
    csv_writer.writerow(['sat_id', 'unclassified_az', 'unclassified_el', 'unclassified_dist', 'classified_az', 'classified_el', 'classified_dist', 'spacetrack_az', 'spacetrack_el', 'spacetrack_dist', 'theta_offset'])

    #gbt pointing
    az1 = 360.0 * u.deg
    el1 = 78.0 * u.deg

    for i, sat_id in enumerate(satellite_idArray) :
        unclassified_TLE = unclassified_TLE_map[sat_id]
        classified_TLE = classified_TLE_map[sat_id]
        spacetrack_TLE = spacetrack_TLE_map[sat_id]
        #use minute by minute time for highest accuracy position calculations
        satTime = timeArray[i]
        satHour = int(satTime.split(":")[0]) + 12 #assume PM time
        satMinute = int(satTime.split(":")[1])
        satSecond = 15 * (i % 4) #15 second intervals
        dt = datetime.datetime(int(satYear), int(satMonth), int(satDay), satHour, satMinute, satSecond) #time of day
        obstime = time.Time(dt)

        #use the TLE and time to calculate azimuth, elevation, and distance using each TLE
        print(f"Calculating position of STARLINK-{sat_id} at {satTime}")
        satname, sat = satellite.get_sat(unclassified_TLE)
        unclassified_az, unclassified_el, unclassified_dist = sat_obs.azel_from_sat(sat, obstime)  
        satname, sat = satellite.get_sat(classified_TLE)
        classified_az, classified_el, classified_dist = sat_obs.azel_from_sat(sat, obstime)  
        satname, sat = satellite.get_sat(spacetrack_TLE)
        spacetrack_az, spacetrack_el, spacetrack_dist = sat_obs.azel_from_sat(sat, obstime)  

        #satellite 
        az2 = spacetrack_az
        el2 = spacetrack_el
        theta_offset = np.arccos(np.sin(el1) * np.sin(el2) + np.cos(el1) * np.cos(el2) * np.cos(az1 - az2))

        #write position data to csv
        csv_writer.writerow([sat_id, unclassified_az, unclassified_el, unclassified_dist, classified_az, classified_el, classified_dist, spacetrack_az, spacetrack_el, spacetrack_dist, theta_offset])