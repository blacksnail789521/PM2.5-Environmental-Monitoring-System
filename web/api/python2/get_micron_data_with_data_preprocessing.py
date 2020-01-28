"""
@author: Ching Chang

api_description:
    get micron data with data preprocessing

for python api:
    function name:
        get_micron_data_with_data_preprocessing
    input:
        table: str
        param: str
        startD: str
        endD: str
        startT: str
        endT: str
    output:
        value: list of float
        timestamp: list of datetime.datetime
"""



import json
import csv
import datetime as dt

from get_micron_data import getData



def get_micron_data_with_data_preprocessing(table, param, startD, endD, startT, endT):
    
    # get data
    
    data = getData(table, param, startD, endD, startT, endT)
    
    with open('micron_data.json','w') as data_file:
        data_file.write(data)
    
    data = json.loads(data)
    
    
    # data preprocessing
    
    timestamp = []
    value = []
    
    for record in data:
        timestamp.append(dt.datetime.strptime(record["d"] + record["t"], "%Y-%m-%d%H:%M:%S"))
        value.append(record["value"])
    
    
    return timestamp, value



if __name__ == "__main__":
    
    # call function
    
    table = "host100"
    param = "param9822"
    startD = "2016-11-21"
    endD = "2017-01-04"
    #startT = "23:35:26"
    #endT = "23:59:24"
    startT = "00:00:00.000000"
    endT = "23:59:59.000000"
    
    timestamp, value = get_micron_data_with_data_preprocessing(table, param, startD, endD, startT, endT)
    
    with open('01-full_data.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp", "value"])
        for i in range(len(timestamp)):
            writer.writerow([timestamp[i], value[i]])
    
    with open('02-timestamp.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for element in timestamp:
            writer.writerow([element])
            
    with open('03-value.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for element in value:
            writer.writerow([element])