import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import matplotlib.pyplot as plt


start_time = time.time()

########## data preprocessing #################################################

with open('data.json') as data_file:     
    raw_data = json.load(data_file)

data = []

i = 0
for element in raw_data:
    data.append([])
    data[i].append(dt.datetime.strptime(element, "%Y-%m-%d_%H:%M:%S"))
    data[i].append(raw_data[element]["pm25"])
    data[i].append(raw_data[element]["t"])
    data[i].append(raw_data[element]["h"])
    i = i + 1

data.sort(key = itemgetter(0), reverse = False)

final_data = []
buf = []
start = data[0][0]
delta = dt.timedelta(minutes = 5)
slidewindow = start

i = 0   #data index
j = 0   #final_data index
k = 0   #buffer index
while 1:
    if i == len(data):
        final_data.append([])
        final_data[j].append(slidewindow)
        final_data[j].append(np.mean(buf, axis = 0)[0])
        final_data[j].append(np.mean(buf, axis = 0)[1])
        final_data[j].append(np.mean(buf, axis = 0)[2])
        del buf[:]
        break
    
    if data[i][0] - slidewindow < delta:
        buf.append([])
        buf[k].append(data[i][1])
        buf[k].append(data[i][2])
        buf[k].append(data[i][3])
        i = i + 1
        k = k + 1
    else:
        if buf:
            final_data.append([])
            final_data[j].append(slidewindow)
            final_data[j].append(np.mean(buf, axis = 0)[0])
            final_data[j].append(np.mean(buf, axis = 0)[1])
            final_data[j].append(np.mean(buf, axis = 0)[2])
            j = j + 1
            del buf[:]
            k = 0
            slidewindow = slidewindow + delta
        else:
            final_data.append([])
            final_data[j].append(slidewindow)
            final_data[j].append(final_data[j - 1][1])
            final_data[j].append(final_data[j - 1][2])
            final_data[j].append(final_data[j - 1][3])
            j = j + 1
            slidewindow = slidewindow + delta

            
            
########## matrixprofile ######################################################          
            
def distanceprofile_preprocessing(data, query_length):
    data_length = len(data)
    
    for i in range(len(data)):
        data.append(0)
    
    data_freq = np.fft.fft(data)
    
    data_cum_sum = np.cumsum(data)
    data_cum_sum2 = np.cumsum(np.power(data, 2))
    
    data_sum2 = data_cum_sum2[query_length - 1 : data_length]       \
                - (np.insert(data_cum_sum2[0 : data_length - query_length], 0, 0))
    data_sum = data_cum_sum[query_length - 1 : data_length]        \
                - (np.insert(data_cum_sum[0 : data_length - query_length], 0, 0))

    data_mean = np.divide(data_sum, float(query_length))
    
    data_sigma2 = np.divide(data_sum2, float(query_length)) - np.power(data_mean, 2)
    data_sigma = np.sqrt(data_sigma2)
    
    return data_freq, data_sum2, data_sum, data_mean, data_sigma2, data_sigma


def distanceprofile_mass(query, data_freq, data_length, data_sum2, data_sum, data_mean,  \
                    data_sigma2, data_sigma):
    query_length = len(query)
    
    query = np.divide(np.subtract(query, np.mean(query)), np.std(query))
    query = query.tolist()
    
    query = query[::-1]
    while len(query) < 2 * data_length:
        query.append(0)
    
    query_freq = np.fft.fft(query)
    dataquery = np.fft.ifft(np.multiply(data_freq, query_freq))

    query_sum = np.sum(query)
    query_sum2 = np.sum(np.power(query, 2))

    distanceprofile = np.divide((data_sum2 - 2 * np.multiply(data_sum, data_mean) \
                       + query_length * np.power(data_mean, 2)), data_sigma2)     \
                       - np.divide(2 * dataquery[query_length - 1 : data_length]   \
                       - np.multiply(query_sum, data_mean), data_sigma) + query_sum2
    distanceprofile = np.abs(np.sqrt(distanceprofile))
    
    distanceprofile = distanceprofile.tolist()

    return distanceprofile


def distanceprofile_ed(data, query_index, query_length):
    query = data[query_index : query_index + query_length]
    
    distanceprofile = []

    for i in range(len(data) - query_length + 1):
        query_compare = data[i : i + query_length]
        distanceprofile.append(np.linalg.norm(np.asarray(query) - np.asarray(query_compare)))
    
    return distanceprofile

    
def updatematrixprofile(distance_profile, matrix_profile, matrix_profile_index, data_length, query_length, query_index):
    for i in range(data_length - query_length + 1):
        if distance_profile[i] < matrix_profile[i]:
            matrix_profile[i] = distance_profile[i]
            matrix_profile_index[i] = query_index
    
    
def matrixprofile(data, query_length, method):
    data_function = data[:]
    data_freq, data_sum2, data_sum, data_mean, data_sigma2, data_sigma = \
    distanceprofile_preprocessing(data_function, query_length)
       
    distance_profile = []

    exclusion_zone = int(round(query_length / 2.0))
    
    for i in range(len(data) - query_length + 1):
        '''
        if i % 500 == 0:
            pprint(i)
        '''
        if method == 0:
            distance_profile.append(distanceprofile_mass(data[i : i + query_length], data_freq, \
                                                    len(data), data_sum2, data_sum, \
                                                    data_mean, data_sigma2, data_sigma))
        elif method == 1:
            distance_profile.append(distanceprofile_ed(data, i, query_length))
            
        start = max(0, i - exclusion_zone)
        end = min(len(data) - query_length + 1, i + exclusion_zone + 1)
        distance_profile[i][start : end] = [float("Inf")] * (end - start)
    
    print("--- %s seconds ---" % (time.time() - start_time))
       
    random_array = list(range(0, len(data) - query_length + 1))
    random.shuffle(random_array)
 
    matrix_profile = [float("Inf")] * (len(data) - query_length + 1)
    matrix_profile_index = [-1] * (len(data) - query_length + 1)
  
    for i in random_array:
        updatematrixprofile(distance_profile[i], matrix_profile, matrix_profile_index, \
                            len(data), query_length, i)    

    matrix_profile_and_index_sort = []
    for i in range(len(data) - query_length + 1):
        matrix_profile_and_index_sort.append([])
        matrix_profile_and_index_sort[i].append(matrix_profile[i])
        matrix_profile_and_index_sort[i].append(matrix_profile_index[i])

    matrix_profile_and_index_sort.sort(key = itemgetter(0), reverse = False)
        
    print("--- %s seconds ---" % (time.time() - start_time))
        
    motif_index = []
    discord_index = []
    
    i = 0
    j = 0
    while i < 3:
        legel = True
        
        for element in motif_index:
            if abs(element[0] - matrix_profile_and_index_sort[j][1]) < exclusion_zone or \
               abs(element[1] - matrix_profile_and_index_sort[j][1]) < exclusion_zone:
                j = j + 1
                legel = False
                
        if legel == True:      
            motif_index.append([])
            motif_index[i].append(matrix_profile_and_index_sort[j][1])
            motif_index[i].append(matrix_profile_index[matrix_profile_and_index_sort[j][1]])
            
            i = i + 1
            j = j + 1
            
    i = 0
    j = 0
    while i < 3:
        legel = True
        
        if matrix_profile_and_index_sort[len(matrix_profile_and_index_sort) - j - 1][1] == -1:
            j = j + 1
            legel = False
            
        for element in discord_index:
            if abs(element - matrix_profile_and_index_sort[j][1]) < exclusion_zone:
                j = j + 1
                legel = False
                
        if legel == True:      
            discord_index.append(matrix_profile_and_index_sort[len(matrix_profile_and_index_sort) - j - 1][1])
            
            i = i + 1
            j = j + 1       
    
    return matrix_profile, matrix_profile_index, motif_index, discord_index






########## main ###############################################################


pm25 = []
for i in range(len(final_data)):
    pm25.append(final_data[i][1])
    

i = 0
pm25_csv = []    
with open('pm25.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
    for row in reader:
        pm25_csv.append(int(row[0]))
        i = i + 1
        #pprint(i)
    
    
#pm25_function = pm25[:]
pm25_function = pm25_csv[:]
query_length = 12
method = 0

if query_length > len(pm25) / 20 or query_length < 4:
    pprint("Illegal query_length")

matrix_profile, matrix_profile_index, motif_index, discord_index = matrixprofile(pm25_function, query_length, method)

print("--- %s seconds ---" % (time.time() - start_time))

with open('matrixprofile.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(matrix_profile)):
        writer.writerow([matrix_profile[i]])
        
with open('matrixprofileindex.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(matrix_profile_index)):
        writer.writerow([matrix_profile_index[i]])
    
with open('motifindex.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(motif_index)):
        writer.writerow([motif_index[i]])
        
with open('discordindex.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(discord_index)):
        writer.writerow([discord_index[i]])        

        


        
for i in range(3):
    plt.plot(pm25_function[motif_index[i][0] : motif_index[i][0] + query_length + 1])
    plt.plot(pm25_function[motif_index[i][1] : motif_index[i][1] + query_length + 1])
    plt.show()
            
for i in range(3):
    plt.plot(pm25_function[discord_index[i] : discord_index[i] + query_length + 1])
    plt.show()           
            



print("--- %s seconds ---" % (time.time() - start_time))


