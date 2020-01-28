# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 12:15:01 2016

@author: Hector
"""

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
        current_date = datetime.datetime.now()
        
        
        year,month,day, hour, minute = current_date.year, current_date.month, current_date.day, current_date.hour, (current_date.minute)
        output_file = open('../wind_data_update/%s-%s-%s(%s-%s).txt'%(year,month,day,hour, minute),'w')
        url = "http://opendata2.epa.gov.tw/AQX.json"
        response = urllib.urlopen(url)
        json_data = json.loads(str(response.read()))
        primer = True
        for point in json_data:
            keys =['Status','PSI','CO','PM10','NO','MajorPollutant','WindDirec', 'FPMI','PublishTime','SO2','County','SiteName','WindSpeed','PM2.5','NOx','O3','NO2']
            PM25 = point['PM2.5']
            siteName = point['SiteName']
            county = point['SiteName']
            for key in keys:
                try:
                    if primer:
                        write = str(point[key])
                        primer = False
                    else:
                        write = ',' + str(point[key])
                except:
                    if primer:
                        write = (point[key].encode('utf8'))
                        primer = False
                    else:
                       write = ',' +(point[key].encode('utf8')) 
                       
                output_file.write(write)
            primer = True
            output_file.write("\n")
    
        
            
        output_file.close() 
        
        time.sleep(3600)


main()