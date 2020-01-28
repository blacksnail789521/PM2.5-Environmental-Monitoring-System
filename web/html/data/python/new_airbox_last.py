# -*- coding: utf-8 -*-

import urllib2
import urllib
import csv
import os

import datetime
import requests
import json
import time


def main():
    
    while True:
        
        current_date = datetime.date.today()
        year,month,date = str(current_date).split('-')
        output_file = open('../new_history_data/%s-%s-%s.txt'%(year,month,date),'w')

        while datetime.date.today() == current_date:
            start_time = time.time()
            
            url = "http://nrl.iis.sinica.edu.tw/LASS/last-all-airbox.json"
            

            response = urllib.urlopen(url)
            json_data = json.loads(str(response.read()))

            data = json_data['feeds']

            for point in data:
                #'gps_lat','gps_lon','timestamp','device_id','s_d0','s_h0','s_t0','SiteName','gps_num'
                keys =['device_id','gps_lat','gps_lon','timestamp','s_d0','s_h0','s_t0']
                lat = point['gps_lat']
                lon = point['gps_lon']
                #date,time  = point['timestamp'].split("T")
                datatime = point['timestamp']
                device_id = point['device_id']
                PM25 = point['s_d0']
                humidity = point['s_h0']
                temperature = point['s_t0']


                write = [str(point[key]) for key in keys]
                output_file.write(",".join(write))
		output_file.write(","+point['SiteName'].encode("UTF-8"))
                output_file.write("\n")

            time.sleep(300-(time.time()-start_time))
        
        output_file.close()
    

        

if __name__ == "__main__":
    main()
