
#Parses the channel data from a .txt file
def parsefile(filepath) :
    channeldataArray = []

    #parse channel data
    with open(filepath, 'r') as ifile :
        header = ifile.readline()
        while (1) :
            line = ifile.readline()
            data = line.split()
            #end of file condition
            length = len(data)
            if (length != 3) : break

            #channel num, freq min, and freq max
            channelNum, freq_min, freq_max = data
            channeldataArray.append([channelNum, float(freq_min), float(freq_max)])
    return (channeldataArray)