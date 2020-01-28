import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import matplotlib.pyplot as plt

from data_preprocessing import data_preprocessing
from average_max_min_time_slot import average_max_min_time_slot
from average_max_min_time_mode import average_max_min_time_mode
from matrix_profile import matrixprofile





def create_profile(device_id, start_date, end_date, sample_rate, time_slot, time_mode, query_length, distance_function, k):
    
    # data preprocessing
    
    data_preprocessing(device_id, start_date, end_date, sample_rate)
    
    
    
    # get data
    
    data = []
    with open('data\\data.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
        i = 0
        for row in reader:
            data.append([])
            data[i].append(str(row[0]))
            data[i].append(int(row[1]))
            data[i].append(int(row[2]))
            data[i].append(int(row[3]))
            i = i + 1
    
    pm25 = []
    timestamp = []
    for i in range(len(data)):
        pm25.append(data[i][1])
        timestamp.append(data[i][0])
    
    data_function = pm25[:]
    timestamp_function = timestamp[:]
    
    
    
    # average_max_min_time_slot
    
    average_data, max_data, min_data, timestamp_middle = average_max_min_time_slot(data_function, timestamp_function, time_slot)
    
    
    
    # average_max_min_time_mode
    
    average_data, max_data, min_data = average_max_min_time_mode(data_function, time_mode, sample_rate)
    
    
    
    # matrixprofile
    
    matrix_profile, matrix_profile_index, motif_index, discord_index = matrixprofile(data_function, query_length, distance_function, k)
    




