"""
@author: Ching Chang

api_description:
    store real time data and history data for all sensor

for python api:
    function name:
        store_data
    input:
        
    output:
        data: list
            output_json_file_airbox: str (json file for airbox)
            output_json_file_lass: str (json file for lass)
            output_json_file_epa: str (json file for epa)

for web api:   
    function name:
        get_real_time_data_web
    input:
        
    output:
        output_json_file: str
            keys = airbox, lass, temperature, epa
            subkeys = lat, lon, device_id, pm25, humidity, temperature, name, timestamp
for script:
    run command:
        nohup python3 get_real_time_data.py &
    kill command:
        ps aux | grep python3
        # check for the relevant PID
        kill <relevantPID>
"""



import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import requests
from pathlib import Path
import logging
import os



def store_real_time_data_and_return_device_id_list():
    
    # declare device_id_list
    
    device_id_list = []
    
    
    # airbox
    
    res = requests.get("https://pm25.lass-net.org/data/last-all-airbox.json")
    
    if (res.json()):
        input_json_file = res.json()['feeds']
        output_json_file_airbox = []
            
        
        for i in range(len(input_json_file)):
            data = {}
            data['lat'] = input_json_file[i]['gps_lat']
            data['lon'] = input_json_file[i]['gps_lon']
            data['device_id'] = input_json_file[i]['device_id']
            data['pm25'] = input_json_file[i]['s_d0']
            
            if 's_h0' not in input_json_file[i]:
                continue
            else:
                data['humidity'] = input_json_file[i]['s_h0']
            
            if 's_t0' not in input_json_file[i]:
                continue
            else:
                data['temperature'] = input_json_file[i]['s_t0']
            
            data['name'] = input_json_file[i]['device']
            #data['timestamp'] = input_json_file[i]['timestamp'].replace("T", " ").replace("Z", "")
            data['timestamp'] = str(dt.datetime.strptime(input_json_file[i]['timestamp'], "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(hours=8))
            
            output_json_file_airbox.append(data)
            
            device_id_list.append(data['device_id'])
    
    
    # lass
    
    res = requests.get("https://pm25.lass-net.org/data/last-all-lass.json")
    
    if (res.json()):
        input_json_file = res.json()['feeds']
        output_json_file_lass = []
            
        
        for i in range(len(input_json_file)):
            data = {}
            data['lat'] = input_json_file[i]['gps_lat']
            data['lon'] = input_json_file[i]['gps_lon']
            data['device_id'] = input_json_file[i]['device_id']
            data['pm25'] = input_json_file[i]['s_d0']
            
            if 's_h0' not in input_json_file[i]:
                continue
            else:
                data['humidity'] = input_json_file[i]['s_h0']
            
            if 's_t0' not in input_json_file[i]:
                continue
            else:
                data['temperature'] = input_json_file[i]['s_t0']
            
            if 'device' not in input_json_file[i]:
                data['name'] = input_json_file[i]['device_id']
            else:
                data['name'] = input_json_file[i]['device']
            
            data['timestamp'] = str(dt.datetime.strptime(input_json_file[i]['timestamp'], "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(hours=8))
            
            output_json_file_lass.append(data)
            
            device_id_list.append(data['device_id'])
    
    
    # epa
    
    res = requests.get("https://pm25.lass-net.org/data/last-all-epa.json")
    
    if (res.json()):
        input_json_file = res.json()['feeds']
        output_json_file_epa = []
            
        
        for i in range(len(input_json_file)):
            data = {}
            data['lat'] = input_json_file[i]['gps_lat']
            data['lon'] = input_json_file[i]['gps_lon']
            data['device_id'] = input_json_file[i]['SiteEngName']
            
            if 'PM2_5' not in input_json_file[i]:
                continue
            else:
                data['pm25'] = input_json_file[i]['PM2_5']
                
            data['humidity'] = ""
            data['temperature'] = ""
            
            data['name'] = input_json_file[i]['SiteName']
            data['timestamp'] = input_json_file[i]['timestamp'].replace("T", " ").replace("Z", "")
            
            output_json_file_epa.append(data)
    
    
    
    
    return device_id_list



def store_history_data(device_id_list):
    
    for device_id in device_id_list:

        for i in range(30):
            
            current_date = dt.datetime.now().date() - dt.timedelta(days = 30 - i)
    
            # web crawler
            
            res = requests.get("https://pm25.lass-net.org/data/history-date.php?device_id=" + device_id + "&date=" + current_date)
            
            input_json_file = {}
            if not res.json()['feeds']:
                # no data
                #print(date + " : no data")
                return "no data"
            
            if 'AirBox' in res.json()['feeds'][0]:
                input_json_file = res.json()['feeds'][0]["AirBox"]
            elif 'LASS' in res.json()['feeds'][0]:
                input_json_file = res.json()['feeds'][0]["LASS"]
    


def store_data():
        
    device_id_list = store_real_time_data_and_return_device_id_list()
    
    print(device_id_list)


      
if __name__ == "__main__":
    
    store_data()
        