import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import matplotlib.pyplot as plt
import requests



def daily_data_preprocessing(device_id, date, sample_rate):
    
    # web crawler
    
    res = requests.get("https://pm25.lass-net.org/data/history-date.php?device_id=" + device_id + "&date=" + date)
    
    input_json_file = {}
    if not res.json()['feeds']:
        # no data
        #print date + " : no data"
        return "no data"
    
    if 'AirBox' in res.json()['feeds'][0]:
        raw_data = res.json()['feeds'][0]["AirBox"]
    elif 'LASS' in res.json()['feeds'][0]:
        raw_data = res.json()['feeds'][0]["AirBox"]
        
        
        
        
    
    data_file = open("data\\" + date + ".json", "w")
    data_file.write(res.text)
    data_file.close()
    
    
    
    # load json
    
    with open("data\\" + date + ".json") as data_file:
        raw_data = json.load(data_file)
        raw_data = raw_data["feeds"][0]["AirBox"]
    
    
    
    # get timestamp, pm25, temperature, humidity
    
    data = []
    
    i = 0
    for element in raw_data:
        data.append([])
        data[i].append(dt.datetime.strptime(element, "%Y-%m-%dT%H:%M:%SZ"))
        data[i].append(int(raw_data[element]["s_d0"]))
        data[i].append(int(raw_data[element]["s_t0"]))
        data[i].append(int(raw_data[element]["s_h0"]))
        i = i + 1
    
    
    
    # sort with timestamp
    
    data.sort(key = itemgetter(0), reverse = False)
    
    
    
    # align head of timestamp (start at 00:00:00) and fill the missing items (copy the first value)
    
    final_data = []
    buf = []
    start = dt.datetime.strptime(date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    
    delta_int = sample_rate
    delta = dt.timedelta(minutes = delta_int)
    slidewindow = start
    
    
    i = 0   #data index
    j = 0   #final_data index
    k = 0   #buffer index
    
    while slidewindow < data[0][0]:
        final_data.append([])
        final_data[j].append(slidewindow)
        final_data[j].append(data[0][1])
        final_data[j].append(data[0][2])
        final_data[j].append(data[0][3])
        j = j + 1
        slidewindow = slidewindow + delta
    
    
    # fill the missing items of the original data (copy the previous value)
    
    while 1:
        if i == len(data):
            final_data.append([])
            final_data[j].append(slidewindow)
            final_data[j].append(int(np.mean(buf, axis = 0)[0]))
            final_data[j].append(int(np.mean(buf, axis = 0)[1]))
            final_data[j].append(int(np.mean(buf, axis = 0)[2]))
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
                final_data[j].append(int(np.mean(buf, axis = 0)[0]))
                final_data[j].append(int(np.mean(buf, axis = 0)[1]))
                final_data[j].append(int(np.mean(buf, axis = 0)[2]))
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
    
    
    
    # align tail of timestamp (ex: end at 23:55:00) and fill the missing items (copy the last value)
    
    final_data_end_timestamp = dt.datetime.strptime(date + " 23:"+ str( 60 - (delta_int if 1440 % delta_int == 0 else 1440 - (1440/delta_int)*delta_int) ) + ":00", "%Y-%m-%d %H:%M:%S")
    
    while final_data[len(final_data) - 1][0] < final_data_end_timestamp:
        slidewindow = slidewindow + delta
        final_data.append([])
        final_data[len(final_data) - 1].append(slidewindow)
        final_data[len(final_data) - 1].append(final_data[len(final_data) - 2][1])
        final_data[len(final_data) - 1].append(final_data[len(final_data) - 2][2])
        final_data[len(final_data) - 1].append(final_data[len(final_data) - 2][3])
    
    
    return final_data