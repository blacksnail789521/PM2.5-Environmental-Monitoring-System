"""
@author: Ching Chang

api_description:
    get recent data for one device without unified sample_rate

for python api:
    function name:
        get_recent_data
    input:
        device_id: str
    output:
        data: list of dict (timestamp, pm25, temperature, humidity)
        
for web api:   
    function name:
        get_recent_data_web
    input:
        device_id: str
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



def get_recent_data(device_id):
    
    # web crawler
    
    res = requests.get("https://pm25.lass-net.org/data/history.php?device_id=" + device_id)

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
        data[i]["timestamp"] = dt.datetime.strptime(record, "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(hours = 8)
        data[i]["pm25"] = int(input_json_file[record]["s_d0"])
        data[i]["temperature"] = int(input_json_file[record]["s_t0"])
        data[i]["humidity"] = int(input_json_file[record]["s_h0"])
        i = i + 1
    
    
    # sort with timestamp
    
    data = sorted(data, key = operator.itemgetter("timestamp"), reverse = False)
    
        
    return data
        
        
    '''
    # epa
    if 'EPA' in res.json()['feeds'][0]:
        
        input_json_file = res.json()['feeds']
        output_json_file = []
            
        
        for i in range(len(input_json_file)):
            data = {}
            data['lat'] = input_json_file[i]['gps_lat']
            data['lon'] = input_json_file[i]['gps_lon']
            data['device_id'] = ""
            
            if 'PM2_5' not in input_json_file[i]:
                continue
            else:
                data['s_d0'] = input_json_file[i]['PM2_5']
                
            data['s_h0'] = ""
            data['s_t0'] = ""
            
            data['name'] = input_json_file[i]['SiteName']
            data['timestamp'] = input_json_file[i]['timestamp'].replace("T", " ").replace("Z", "")
            
            
            output_json_file.append(data)
                
                
        return json.dumps({"epa" : output_json_file})
    '''


def get_recent_data_web(device_id):
    
    # call function
    
    data = get_recent_data(device_id)

    
    # return data as json file
    
    for i in range(len(data)):     
        data[i]["timestamp"] = str(data[i]["timestamp"])
    
    output_json_file = json.dumps(data)
    
    
    return output_json_file



if __name__ == "__main__":
    
    # initial start_time for calculating spending time
    
    start_time = time.time()
    
    
    # call function
    
    device_id = "74DA3895C2F0"
    #device_id = "FT3_022_1"
    
    data = get_recent_data(device_id)
    
    
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