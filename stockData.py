# lmarolda - term project
# stock data

# from csv files, need to store stock data as 2D list database of floats
# represented as:      0     1    2     3     4     5      6
# stock AAPL --> [ [ open, high, low, close, adj close, volume ] ]
# where each list is one day of data. each list should be length 252 

import csv

def csvToList(file):
    with open(file, newline= '') as csvfile:
        reader = csv.reader(csvfile)
        rawData = list(reader)
        # do not need the first element because it is not data we want
        data = rawData[1:]
        dataLength = len(data)
    for row in range(dataLength):
        currentDay = data[row]
        # do not need the date, so get rid of this data for each day
        currentDay.pop(0)
        dayDataLength = len(currentDay)
        # now we want to convert each piece of string data to a float
        for col in range(dayDataLength):
            value = currentDay[col]
            # convert each value to float
            floatVersion = float(value)
            # reassign the value in the list to the float version
            currentDay[col] = floatVersion
    return data

# apple data
aapl_2008 = csvToList('AAPL_2008.csv')
aapl_2011 = csvToList('AAPL_2011.csv')
aapl_2015 = csvToList('AAPL_2015.csv')
aapl_2018 = csvToList('AAPL_2018.csv')

# general electric data
ge_2008 = csvToList('GE_2008.csv')
ge_2011 = csvToList('GE_2011.csv')
ge_2015 = csvToList('GE_2015.csv')
ge_2018 = csvToList('GE_2018.csv')

# disney data
dis_2008 = csvToList('DIS_2008.csv')
dis_2011 = csvToList('DIS_2011.csv')
dis_2015 = csvToList('DIS_2015.csv')
dis_2018 = csvToList('DIS_2018.csv')