import requests
import json
import time

def main():
    while True:
        
        try:
            
            # airbox
            res = requests.get("https://pm25.lass-net.org/data/last-all-airbox.json")
            
            if (res.json()):
                input_json_file = res.json()['feeds']
                output_json_file_1 = []
                    
                
                for i in range(len(input_json_file)):
                    data = {}
                    data['lat'] = input_json_file[i]['gps_lat']
                    data['lon'] = input_json_file[i]['gps_lon']
                    data['device_id'] = input_json_file[i]['device_id']
                    data['s_d0'] = input_json_file[i]['s_d0']
                    
                    if 's_h0' not in input_json_file[i]:
                        continue
                    else:
                        data['s_h0'] = input_json_file[i]['s_h0']
                    
                    if 's_t0' not in input_json_file[i]:
                        continue
                    else:
                        data['s_t0'] = input_json_file[i]['s_t0']
                    
                    data['name'] = input_json_file[i]['device']
                    data['timestamp'] = input_json_file[i]['timestamp'].replace("T", " ").replace("Z", "")
                    
                    
                    output_json_file_1.append(data)
            
            
            # lass
            res = requests.get("https://pm25.lass-net.org/data/last-all-lass.json")
            
            if (res.json()):
                input_json_file = res.json()['feeds']
                output_json_file_2 = []
                    
                
                for i in range(len(input_json_file)):
                    data = {}
                    data['lat'] = input_json_file[i]['gps_lat']
                    data['lon'] = input_json_file[i]['gps_lon']
                    data['device_id'] = input_json_file[i]['device_id']
                    data['s_d0'] = input_json_file[i]['s_d0']
                    
                    if 's_h0' not in input_json_file[i]:
                        continue
                    else:
                        data['s_h0'] = input_json_file[i]['s_h0']
                    
                    if 's_t0' not in input_json_file[i]:
                        continue
                    else:
                        data['s_t0'] = input_json_file[i]['s_t0']
                    
                    if 'device' not in input_json_file[i]:
                        data['name'] = input_json_file[i]['device_id']
                    else:
                        data['name'] = input_json_file[i]['device']
                    
                    data['timestamp'] = input_json_file[i]['timestamp'].replace("T", " ").replace("Z", "")
                    
                    
                    output_json_file_2.append(data)
            
            
            # epa
            res = requests.get("https://pm25.lass-net.org/data/last-all-epa.json")
            
            if (res.json()):
                input_json_file = res.json()['feeds']
                output_json_file_3 = []
                    
                
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
                    
                    
                    output_json_file_3.append(data)
            
        
            data_file = open('../real_time_data/all.json','w')
            data_file.write(json.dumps({"airbox" : output_json_file_1, "lass" : output_json_file_2, "epa" : output_json_file_3}))
            data_file.close()
            
            data_file = open('../real_time_data/airbox.json','w')
            data_file.write(json.dumps({"airbox" : output_json_file_1}))
            data_file.close()
            
            data_file = open('../real_time_data/lass.json','w')
            data_file.write(json.dumps({"lass" : output_json_file_2}))
            data_file.close()
            
            data_file = open('../real_time_data/epa.json','w')
            data_file.write(json.dumps({"epa" : output_json_file_3}))
            data_file.close()
            
            #every 5 min
            time.sleep(5 * 60)
        
        except:
            pass
        


main()