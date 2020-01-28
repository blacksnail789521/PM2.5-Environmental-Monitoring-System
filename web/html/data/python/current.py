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
        url = "http://nrl.iis.sinica.edu.tw/LASS/last-all-airbox.json"
        response = urllib.urlopen(url)
        json_data = json.loads(str(response.read()))

        output_file = open('../current/current.json','w')
        json.dump(json_data,output_file)
        output_file.close()
        time.sleep(300)
    
if __name__ == "__main__":
    main()
