
import datetime

#Parses the timestamps from a .txt file and converts them to event timestamp data
def parsefile(filepath) :
    eventnames =  []
    eventdatetimes = []

    #parse event timestamp data 
    with open(filepath, 'r') as efile :
        header = efile.readline()
        while (1) :
            line = efile.readline()
            data = line.split()
            #end of file condition
            length = len(data)
            if (length != 3) : break

            #event name, date, time, and format
            eventname = data[0]
            eventnames.append(eventname)

            eventYear, eventMonth, eventDay = tuple(map(int, data[1].split('-'))) #split into [y,m,d]
            
            eventHour, eventMinute, eventSecond = tuple(map(int, data[2].split(':'))) #split into [h,m,s]

            eventdatetimes.append(datetime.datetime(eventYear, eventMonth , eventDay, eventHour, eventMinute, eventSecond))
    
    return (eventnames, eventdatetimes)