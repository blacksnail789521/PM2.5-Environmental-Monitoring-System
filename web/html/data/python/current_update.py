#
#-*- coding: utf-8 -*-

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
		#url = "http://nrl.iis.sinica.edu.tw/LASS/last-all-airbox.json"
		url = "http://airmap.g0v.asper.tw/json/airmap.json"
		response = urllib.urlopen(url)
		json_data = json.loads(str(response.read()))
		output_file = open('../current_update/current.txt','w')

		for point in json_data:
			if ('Airbox' in point['Maker']):
				#sum = sum + 1
				#[u'SiteName', u'LatLng', u'RawData', u'Data', u'Maker', u'SiteGroup']

				name = point[u'SiteName']
				lat = point[u'LatLng'][u'lat']
				lon = point[u'LatLng'][u'lng']
				date_time = point[u'Data'][u'Create_at']
				device_id = point[u'RawData'][u'id']
				PM25 = point[u'RawData'][u'pm25']
				humidity = point[u'Data'][u'Humidity']
				temperature = point[u'Data'][u'Temperature']

				#print lat,lon,datetime,device_id,PM25,humidity,temperature,name
				write = [str(device_id),str(lat),str(lon),str(date_time),str(PM25),str(humidity),str(temperature),str(name.encode("UTF-8"))]
				output_file.write(",".join(write))
				output_file.write("\n")		
		   
		#json.dump(json_data,output_file)
		output_file.close()
		time.sleep(300)

if __name__ == "__main__":
    main()
	
	
