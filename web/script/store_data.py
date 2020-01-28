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

for script:
    run command:
        nohup python3 store_data.py &
    kill command:
        ps aux | grep python3
        # check for the relevant PID
        kill <relevantPID>
"""



import json
import datetime as dt
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
    
    
    # save as json file
    
    with open('../html/data/real_time_data/airbox.json','w') as data_file:
                data_file.write(json.dumps({"airbox" : output_json_file_airbox}))
            
            
    with open('../html/data/real_time_data/lass.json','w') as data_file:
        data_file.write(json.dumps({"lass" : output_json_file_lass}))
    
    
    if output_json_file_epa != []:
        with open('../html/data/real_time_data/epa.json','w') as data_file:
            data_file.write(json.dumps({"epa" : output_json_file_epa}))
    
    
    with open('../html/data/real_time_data/all.json','w') as data_file:
        
        epa_file = Path("../html/data/real_time_data/epa.json")
        
        if epa_file.is_file():
            with open('../html/data/real_time_data/epa.json','r') as epa:
                epa = json.load(epa)['epa']
                data_file.write(json.dumps({"airbox" : output_json_file_airbox, "lass" : output_json_file_lass, "epa" : epa}))
        else:
            data_file.write(json.dumps({"airbox" : output_json_file_airbox, "lass" : output_json_file_lass, "epa" : []}))
    
    
    return device_id_list



def store_history_data(device_id_list):
    
    for device_id in device_id_list:
        
        # create folder if not exist
        
        os.makedirs("../html/data/history_data/" + device_id, exist_ok = True)
        
        
        # store data for 30 days

        for i in range(30):
            
            date = dt.datetime.now().date() - dt.timedelta(days = 30 - i)
            
            
            # store data if not exist
            
            history_file = Path("../html/data/history_data/" + device_id + "/" + str(date))
    
            if not history_file.is_file():
    
                # web crawler
                
                res = requests.get("https://pm25.lass-net.org/data/history-date.php?device_id=" + device_id + "&date=" + str(date))
                
                input_json_file = {}
                
                if not res.json()['feeds']:
                    # no data
                    pass
                else:
                    if 'AirBox' in res.json()['feeds'][0]:
                        input_json_file = res.json()['feeds'][0]["AirBox"]
                    elif 'LASS' in res.json()['feeds'][0]:
                        input_json_file = res.json()['feeds'][0]["LASS"]
                
                with open("../html/data/history_data/" + device_id + "/" + str(date) + ".json", "w") as json_file:
                    json.dump(input_json_file, json_file)
    


def store_data():
        
    device_id_list = store_real_time_data_and_return_device_id_list()
    
    store_history_data(device_id_list)


      
if __name__ == "__main__":
    
    # set up logging
    
    log_file = Path("store_data.log")
    
    if not log_file.is_file():
        with open("store_data.log", "w"):
            pass
    else:
        os.remove("store_data.log")
        with open("store_data.log", "w"):
            pass
    
    logging.basicConfig(level=logging.DEBUG, filename='store_data.log')
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    
    # call function infinitely time (every 5 min)
    
    while True:
        try:
            store_data()
                
        except Exception as e:
            logging.error(e)
        
        time.sleep(5 * 60)
        