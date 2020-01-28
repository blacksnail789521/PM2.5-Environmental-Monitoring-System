"""
@author: Ching Chang

api_description:
    get specified date of the data for one sensor with unified sample rate

for python api:
    function name:
        get_clean_data
    input:
        device_id: str
        start_date: str
        end_date: str
        sample_rate: int
        days: list
            0 = Sunday, 1 = Monday, ...
        hours: list
            0 = 00:00 ~ 00:59, 1 = 01:00 ~ 01:59, ...
    output:
        data: list of dict (timestamp, pm25, temperature, humidity)

for web api:   
    function name:
        get_clean_data_web
    input:
        device_id: str
        start_date: str
        end_date: str
        sample_rate: int
        days: list
            0 = Sunday, 1 = Monday, ...
        hours: list
            0 = 00:00 ~ 00:59, 1 = 01:00 ~ 01:59, ...
    output:
        output_json_file: str
            keys = timestamp, pm25, temperature, humidity
"""



import json
import csv
import datetime as dt
import operator
import numpy as np
import random
from pprint import pprint
import time
import requests



def daily__get_clean_data(device_id, date, sample_rate, hours):
    
    # web crawler
    
    res = requests.get("https://pm25.lass-net.org/data/history-date.php?device_id=" + device_id + "&date=" + date)
    
    input_json_file = {}
    if not res.json()['feeds']:
        # no data
        #print(date + " : no data")
        return "no data"
    
    if 'AirBox' in res.json()['feeds'][0]:
        input_json_file = res.json()['feeds'][0]["AirBox"]
    elif 'LASS' in res.json()['feeds'][0]:
        input_json_file = res.json()['feeds'][0]["LASS"]
    
    
    # get timestamp, pm25, temperature, humidity
    
    data = []
    
    i = 0
    for record in input_json_file:
        data.append({})
        data[i]["timestamp"] = dt.datetime.strptime(record, "%Y-%m-%dT%H:%M:%SZ")
        data[i]["pm25"] = int(input_json_file[record]["s_d0"])
        data[i]["temperature"] = int(input_json_file[record]["s_t0"])
        data[i]["humidity"] = int(input_json_file[record]["s_h0"])
        i = i + 1
    
    
    # sort with timestamp
    
    data = sorted(data, key = operator.itemgetter("timestamp"), reverse = False)
    
    
    # align head of timestamp (start at 00:00:00) and fill the missing items (copy the first value)
    
    final_data = []
    buf = []    # store the data between two new timestamps
    start = dt.datetime.strptime(date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    
    delta_int = sample_rate
    delta = dt.timedelta(minutes = delta_int)
    slidewindow = start
    
    
    i = 0   # data index
    j = 0   # final_data index
    b = 0   # buffer index
    
    while slidewindow < data[0]["timestamp"]:
        final_data.append({})
        final_data[j]["timestamp"] = slidewindow
        final_data[j]["pm25"] = data[0]["pm25"]
        final_data[j]["temperature"] = data[0]["temperature"]
        final_data[j]["humidity"] = data[0]["humidity"]
        j = j + 1
        slidewindow = slidewindow + delta
    
    
    # unify the sample rate (have data => get average, no data => store None)
    
    while 1:
        if i == len(data):
            final_data.append({})
            final_data[j]["timestamp"] = slidewindow            
            final_data[j]["pm25"] = sum(record["pm25"] for record in buf) // len(buf)
            final_data[j]["temperature"] = sum(record["temperature"] for record in buf) // len(buf)
            final_data[j]["humidity"] = sum(record["humidity"] for record in buf) // len(buf)
            del buf[:]
            break
        
        if data[i]["timestamp"] - slidewindow < delta:
            buf.append({})
            buf[b]["pm25"] = data[i]["pm25"]
            buf[b]["temperature"] = data[i]["temperature"]
            buf[b]["humidity"] = data[i]["humidity"]
            i = i + 1
            b = b + 1
        else:
            if buf:
                final_data.append({})
                final_data[j]["timestamp"] = slidewindow                
                final_data[j]["pm25"] = sum(record["pm25"] for record in buf) // len(buf)
                final_data[j]["temperature"] = sum(record["temperature"] for record in buf) // len(buf)
                final_data[j]["humidity"] = sum(record["humidity"] for record in buf) // len(buf)
                j = j + 1
                del buf[:]
                b = 0
                slidewindow = slidewindow + delta
            else:
                final_data.append({})
                final_data[j]["timestamp"] = slidewindow
                final_data[j]["pm25"] = None
                final_data[j]["temperature"] = None
                final_data[j]["humidity"] = None
                j = j + 1
                slidewindow = slidewindow + delta
    
    
    # align tail of timestamp (ex: end at 23:55:00) and fill the missing items (copy the last value)
    
    last_time_in_minutes = 0
    while (1440 - last_time_in_minutes) > sample_rate:
        last_time_in_minutes += sample_rate
        
    final_data_end_timestamp = dt.datetime.strptime(date + str(last_time_in_minutes // 60) + ":" + str(last_time_in_minutes % 60) + ":00", "%Y-%m-%d%H:%M:%S")
    
    while final_data[len(final_data) - 1]["timestamp"] < final_data_end_timestamp:
        slidewindow = slidewindow + delta
        final_data.append({})
        final_data[len(final_data) - 1]["timestamp"] = slidewindow
        final_data[len(final_data) - 1]["pm25"] = final_data[len(final_data) - 2]["pm25"]
        final_data[len(final_data) - 1]["temperature"] = final_data[len(final_data) - 2]["temperature"]
        final_data[len(final_data) - 1]["humidity"] = final_data[len(final_data) - 2]["humidity"]
    
    
    # use interpolation to update the "None"
    
    buf = []    # store None information, buf[i][0] = start index of None, buf[i][1] = end index of None
    b = 0       # buffer index
    
    for i in range(len(final_data)):
        if final_data[i]["pm25"] == None and final_data[i-1]["pm25"] != None:
            buf.append({})
            buf[b]["start"] = i
        elif final_data[i]["pm25"] != None and final_data[i-1]["pm25"] == None:
            buf[b]["end"] = i - 1
            b = b + 1
    
    for element in buf:
        
        number_of_filled_value = element["end"] - element["start"] + 1
        before_none = final_data[element["start"] - 1]
        after_none = final_data[element["end"] + 1]
        
        for record_index in range(element["start"], element["end"] + 1):
            final_data[record_index]["pm25"] = int( before_none["pm25"] + (record_index - element["start"] + 1) * (after_none["pm25"] - before_none["pm25"]) /  (number_of_filled_value + 1) )
            final_data[record_index]["temperature"] = int( before_none["temperature"] + (record_index - element["start"] + 1) * (after_none["temperature"] - before_none["temperature"]) /  (number_of_filled_value + 1) )
            final_data[record_index]["humidity"] = int( before_none["humidity"] + (record_index - element["start"] + 1) * (after_none["humidity"] - before_none["humidity"]) /  (number_of_filled_value + 1) )
    
    
    # remove the data that time isn't in hours
    
    hours_need_to_remove = [element for element in list(range(0, 24)) if element not in hours]
    
    for element in hours_need_to_remove:
        hours_need_to_remove_start = dt.time(hour = element)
        hours_need_to_remove_end = dt.time(hour = element, minute = 59)
        
        final_data = [record for record in final_data if not (hours_need_to_remove_start <= record["timestamp"].time() and record["timestamp"].time() <= hours_need_to_remove_end)]
    
    
    return final_data



def get_clean_data(device_id, start_date, end_date, sample_rate, days, hours):
    
    # change the type of start_date, end_date to datetime
    
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
    
    
    # initial current_date
    
    current_date = start_date - dt.timedelta(days = 1)
    
    
    # process the data from start_date to end_date
    
    data = []
    while current_date <= end_date:
        current_date_weekday = current_date.isoweekday() if current_date.isoweekday() != 7 else 0
        if current_date_weekday not in days:
            pass
        else:
            #print("processing " + str(current_date).split(" ")[0])
            daily_data = daily__get_clean_data(device_id, str(current_date).split(" ")[0], sample_rate, hours)
            for record in daily_data:
                data.append(record)
        current_date = current_date + dt.timedelta(days = 1)
    
    
    return data



def get_clean_data_web(device_id, start_date, end_date, sample_rate, days, hours):
    
    # call function
    
    data = get_clean_data(device_id, start_date, end_date, sample_rate, days, hours)
    
    
    # return data as json file
    
    for i in range(len(data)):     
        data[i]["timestamp"] = str(data[i]["timestamp"])
    
    output_json_file = json.dumps(data)
    
    
    return output_json_file
    
    

if __name__ == '__main__':
    
    # initial start_time for calculating spending time
    
    start_time = time.time()
    
    
    # call python api
    
    device_id = "74DA3895C2F0"
    start_date = "2017-06-29"
    end_date = "2017-07-03"
    sample_rate = 5
    days = list(range(0, 7))
    #days = [0, 6]
    hours = list(range(0, 24))
    #hours = [21, 22, 23]
    
    data = get_clean_data(device_id, start_date, end_date, sample_rate, days, hours)
    
    
    # save as csv file
    
    with open('test/01-full_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "pm25", "temperature", "humidity"])
        for record in data:
            writer.writerow([record["timestamp"], record["pm25"], record["temperature"], record["humidity"]])
    
    with open('test/02-timestamp.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for record in data:
            writer.writerow([record["timestamp"]])   
            
    with open('test/03-pm25.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for record in data:
            writer.writerow([record["pm25"]])
        
    with open('test/04-temperature.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for record in data:
            writer.writerow([record["temperature"]])
            
    with open('test/05-humidity.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for record in data:
            writer.writerow([record["humidity"]])
    
    
    # show spending time
    
    print("spending time: %s seconds" % (time.time() - start_time))