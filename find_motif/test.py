import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
from pprint import pprint

with open('data.json') as data_file:     
    raw_data = json.load(data_file)

data = []

i = 0
for element in raw_data:
    data.append([])
    data[i].append(dt.datetime.strptime(element, "%Y-%m-%d_%H:%M:%S"))
    data[i].append(raw_data[element]["pm25"])
    data[i].append(raw_data[element]["t"])
    data[i].append(raw_data[element]["h"])
    i = i + 1

data.sort(key = itemgetter(0), reverse = False)



final_data = []
buf = []
start = data[0][0]
delta = dt.timedelta(minutes = 5)
slidewindow = start

i = 0
j = 0
k = 0
while 1:
    if i == len(data):
        final_data.append([])
        final_data[j].append(slidewindow)
        final_data[j].append(np.mean(buf, axis = 0)[0])
        final_data[j].append(np.mean(buf, axis = 0)[1])
        final_data[j].append(np.mean(buf, axis = 0)[2])
        del buf[:]
        break
    
    if data[i][0] - slidewindow < delta:
        buf.append([])
        buf[k].append(data[i][1])
        buf[k].append(data[i][2])
        buf[k].append(data[i][3])
        i = i + 1
        k = k + 1
    else:
        if buf:
            final_data.append([])
            final_data[j].append(slidewindow)
            final_data[j].append(np.mean(buf, axis = 0)[0])
            final_data[j].append(np.mean(buf, axis = 0)[1])
            final_data[j].append(np.mean(buf, axis = 0)[2])
            j = j + 1
            del buf[:]
            k = 0
            slidewindow = slidewindow + delta
        else:
            final_data.append([])
            final_data[j].append(slidewindow)
            final_data[j].append(final_data[j - 1][1])
            final_data[j].append(final_data[j - 1][2])
            final_data[j].append(final_data[j - 1][3])
            j = j + 1
            slidewindow = slidewindow + delta










pprint(final_data)