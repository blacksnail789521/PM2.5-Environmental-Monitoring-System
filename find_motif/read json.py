import json
import csv
from pprint import pprint
import datetime as dt
from operator import itemgetter
import numpy as np

with open('data.json') as data_file:
#with open('data_small.json') as data_file:    
    raw_data = json.load(data_file)
    

    
buf = []
    

data = []

final_data = []

start = dt.datetime(2016, 11, 1, 0, 0, 0)

#print start

end = dt.datetime(2016, 11, 25, 14, 10, 0)

#print end

delta = dt.timedelta(minutes = 5)

slidewindow = start

#end = end + delta

#print end





i = 0

for element in raw_data:
    pm25 = raw_data[element]["pm25"]
    timestamp =  dt.datetime.strptime(element, "%Y-%m-%d_%H:%M:%S")
    
    
    data.append([])
    data[i].append(timestamp)
    data[i].append(pm25)
    i = i + 1


data.sort(key = itemgetter(0), reverse = False)


pprint(data)
