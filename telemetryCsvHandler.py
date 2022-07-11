import csv
import datetime

def __matchFieldsToColumns(headers, fieldList) :
    # populate match map with default 0's
    fieldColMatchMap = {}
    for field in fieldList :
        fieldColMatchMap[field] = 0


    # attempt to match each column to a field
    for current_column in range(len(headers)) :
        for field in fieldList :
            if (field in headers[current_column]) :
                fieldColMatchMap[field] = current_column

    # display the matches
    print("Confirm the following data fields:")
    for field, colnum in fieldColMatchMap.items() :
        print("Matched column <" + headers[colnum] + "> to field: <" + field + ">")

    # prompt user to manually change matches
    answer = input("Are the above fields correct? y/n ")
    while (answer != "y" and answer != "n") :
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
                for field, colnum in fieldColMatchMap.items() :
                    if (field == command[1]) :
                        fieldColMatchMap[field] = int(command[2]) #update colnum corresponding to entered field
            else :
                print("command invalid")

    # display new matches
    for field, colnum in fieldColMatchMap.items() :
        print("Reading in column <" + headers[colnum] + "> for field: <" + field + ">")

    return fieldColMatchMap


def parsefile(telemetryFilepath, fieldList) :
    with open(telemetryFilepath) as csvFile:
        csvReader = csv.reader(csvFile, delimiter = ',')

        # get column headers
        headers = next(csvReader)

        # create list for each data field
        dataListMap = {}
        for field in fieldList :
            dataListMap[field] = []
           
        # match fields
        fieldColMatchMap = __matchFieldsToColumns(headers, fieldList)

        # parse data lines
        for linenum, row in enumerate(csvReader) :
            if (linenum == 0) :
                satDate = row[0].split()[0]
                satYear = int(satDate.split("/")[2])
                satMonth = int(satDate.split("/")[0])
                satDay = int(satDate.split("/")[1])
            satTime = row[fieldColMatchMap["timestamp (GMT+00:00 UTC)"]].split()[1] 
            rx_channel = row[fieldColMatchMap["rx_channel_id"]]  #leave as raw strings
            satellite_id = row[fieldColMatchMap["satellite_id"]]
            theta_offset = row[fieldColMatchMap["theta_offset"]].split()[0]  #get rid of deg string

            # determine datetime for each point
            satHour = int(satTime.split(":")[0])  #UTC time
            satMinute = int(satTime.split(":")[1])
            satSecond = 15 * (linenum % 4) #15 second intervals
            satDatetime = datetime.datetime(satYear, satMonth, satDay, satHour, satMinute, satSecond)

            # store data
            dataListMap["timestamp (GMT+00:00 UTC)"].append(satDatetime) 
            dataListMap["rx_channel_id"].append(rx_channel)  #leave as strings
            dataListMap["satellite_id"].append(satellite_id)
            dataListMap["theta_offset"].append(theta_offset)  #get rid of deg string

        return (linenum+1), dataListMap
        
