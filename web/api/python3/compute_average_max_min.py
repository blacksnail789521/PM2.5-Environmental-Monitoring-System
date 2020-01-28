"""
@author: Ching Chang

api_description:
    compute the average/max/min for the data in a given time mode

for python api:
    function name:
        compute_average_max_min
    input:    
        data: list
        sample_rate: int
        time_mode: str
    output:
        average_data: list
        max_data: list
        min_data: list

for web api:   
    function name:
        compute_average_max_min_web
    input:
        device_id: str
        start_date: str
        end_date: str
        sample_rate: int
        time_mode: str
    output:
        output_json_file: str
            keys = average_data, max_data, min_data
"""



import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import platform

from get_clean_data import get_clean_data
   

 
def compute_average_max_min(data, sample_rate, time_mode):
    
    # compute time_slot (there are "time_slot" points in one "time_mode")
    
    if time_mode == "hour" and len(data) >= 60 // sample_rate:
        time_slot = 60 // sample_rate
    elif time_mode == "day" and len(data) >= 60*24 // sample_rate:
        time_slot = 60*24 // sample_rate
    elif time_mode == "week" and len(data) >= 60*24*7 // sample_rate:
        time_slot = 60*24*7 // sample_rate
    else:
        return 
    
    
    # declare average_data, max_data, min_data as empty dict
    
    average_data = []
    max_data = []
    min_data = []
    
    
    # compute subdata_count
    
    subdata_count = len(data) // time_slot
    
    
    # compute average_data, max_data, min_data (length is equal to "time_slot")
    
    for i in range(time_slot):        
        average_data.append(int(np.sum(data[i : i + time_slot * (subdata_count - 1) + 1 : time_slot])) // subdata_count)
        max_data.append(int(np.max(data[i : i + time_slot * (subdata_count - 1) + 1 : time_slot])))
        min_data.append(int(np.min(data[i : i + time_slot * (subdata_count - 1) + 1 : time_slot])))
    
    
    # return average_data, max_data, min_data as json file
    
    return average_data, max_data, min_data



def compute_average_max_min_web(device_id, start_date, end_date, sample_rate, time_mode):
    
    # get data
    
    days = list(range(0, 7))
    hours = list(range(0, 24))
    
    data = get_clean_data(device_id, start_date, end_date, sample_rate, days, hours)
    
    
    # we choose the pm25 data
    
    pm25 = []
    for record in data:
        pm25.append(record["pm25"])
    
    
    # call function
    
    data = pm25
    
    average_data, max_data, min_data = compute_average_max_min(data, sample_rate, time_mode)
    
    
    # define timestamp
    
    if time_mode == "hour":
        start_time = dt.datetime(2017, 7, 20, 0, 0, 0)
        end_time = dt.datetime(2017, 7, 20, 0, 59, 59)
    elif time_mode == "day":
        start_time = dt.datetime(2017, 7, 20, 0, 0, 0)
        end_time = dt.datetime(2017, 7, 20, 23, 59, 59)
    
    timestamp = []
    current_time = start_time
    
    while current_time < end_time:
        
        if time_mode == "hour":
            timestamp.append(str(dt.time(0, current_time.minute, current_time.second)).replace("00:", "", 1))
        elif time_mode == "day":
            timestamp.append(str(dt.time(current_time.hour, current_time.minute, current_time.second)))
            
        current_time = current_time + dt.timedelta(minutes = sample_rate)
    
    
    # return average_data, max_data, min_data as json file
    
    output_json_file = json.dumps({"average_data" : average_data, "max_data" : max_data, "min_data" : min_data, "timestamp" : timestamp})
    
    return output_json_file

if __name__ == '__main__':
    
    # initial start_time for calculating spending time
    
    start_time = time.time()
    
    
    # get data
    
    device_id = "74DA3895C2F0"
    start_date = "2017-05-10"
    end_date = "2017-05-14"
    sample_rate = 5
    days = list(range(0, 7))
    hours = list(range(0, 24))
    
    data = get_clean_data(device_id, start_date, end_date, sample_rate, days, hours)
    
    
    # we choose the pm25 data
    
    pm25 = []
    for record in data:
        pm25.append(record["pm25"])
    
    
    # call function
    
    data = pm25
    time_mode = "hour"
    
    average_data, max_data, min_data = compute_average_max_min(data, sample_rate, time_mode)
    
    
    # plot (only Windows)
    
    if platform.system() == "Windows":
        
        import matplotlib.pyplot as plt
        
        if time_mode == "hour":
            time_slot = 60 // sample_rate
        elif time_mode == "day":
            time_slot = 60*24 // sample_rate
        elif time_mode == "week":
            time_slot = 60*24*7 // sample_rate
        
        subdata_count = len(data) // time_slot
        
        print("################   compute_average_max_min   ################")
        print("original data:")
        i = 0
        for _ in range(subdata_count):
            plt.plot(data[i : i + time_slot])
            i = i + time_slot
        plt.show()
        
        print("--------------------------------------------------------------")
        print("average data:")
        plt.plot(average_data)
        plt.show()
        
        print("--------------------------------------------------------------")
        print("max data:")
        plt.plot(max_data)
        plt.show()
        
        print("--------------------------------------------------------------")
        print("min data:")
        plt.plot(min_data)
        plt.show()
    
    
    # show spending time
    
    print("spending time: %s seconds" % (time.time() - start_time))