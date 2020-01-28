import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import matplotlib.pyplot as plt

    
def average_max_min_time_slot(data, timestamp, time_slot):
    
    average_data = []
    max_data = []
    min_data = []
    timestamp_middle = []
    
    for i in xrange(0, len(data), time_slot):
        average_data.append(np.sum(data[i : i + time_slot]) / float(len(data[i : i + time_slot])))
        max_data.append(np.max(data[i : i + time_slot]))
        min_data.append(np.min(data[i : i + time_slot]))
        timestamp_middle.append(timestamp[i : i + time_slot][len(timestamp[i : i + time_slot]) / 2])
    
    
    
    # plot
    
    print "################   average_max_min_time_slot   ################"
    print "original data:"
    plt.plot(data)
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
    
    return average_data, max_data, min_data, timestamp_middle