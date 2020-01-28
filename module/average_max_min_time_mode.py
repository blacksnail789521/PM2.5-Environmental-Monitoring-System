import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import matplotlib.pyplot as plt

    
def average_max_min_time_mode(data, time_mode, sample_rate):
    
    if time_mode == "hour":
        time_slot = 24 / sample_rate
    elif time_mode == "day":
        time_slot = 24*60 / sample_rate
    elif time_mode == "week":
        time_slot = 24*60*7 / sample_rate
    
    average_data = []
    max_data = []
    min_data = []
    
    subdata_count = len(data) / time_slot
    
    for i in range(time_slot):
        average_data.append(np.sum(data[i : i + time_slot * (subdata_count - 1) + 1 : time_slot]) / subdata_count)
        max_data.append(np.max(data[i : i + time_slot * (subdata_count - 1) + 1 : time_slot]))
        min_data.append(np.min(data[i : i + time_slot * (subdata_count - 1) + 1 : time_slot]))
    
    
    
    # plot
    
    print "################   average_max_min_time_mode   ################"
    print "original data:"
    i = 0
    for _ in range(subdata_count):
        plt.plot(data[i : i + time_slot])
        i = i + time_slot
    plt.show()
    
    print "--------------------------------------------------------------"
    print "average data:"
    plt.plot(average_data)
    plt.show()
    
    print "--------------------------------------------------------------"
    print "max data:"
    plt.plot(max_data)
    plt.show()
    
    print "--------------------------------------------------------------"
    print "min data:"
    plt.plot(min_data)
    plt.show()
    
    return average_data, max_data, min_data