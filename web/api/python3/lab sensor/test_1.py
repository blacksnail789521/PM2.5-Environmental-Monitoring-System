"""
@author: Ching Chang

api_description:
    compute the "matrix profile" of the data to get the top-k motifs and discords

for python api:
    function name:
        compute_matrix_profile
    input:
        data: list
        query_length: int
        distance_function: str
        number_of_motifs: int
        lower_limit_of_the_number_of_single_motif: int
    output:
        matrix_profile: list
        matrix_profile_index: list
        motif_index: list
        discord_index: list

for web api:   
    function name:
        compute_matrix_profile_web
    input:
        device_id: str
        start_date: str
        end_date: str
        sample_rate: int
        days: list
            0 = Sunday, 1 = Monday, ...
        hours: list
            0 = 00:00 ~ 00:59, 1 = 01:00 ~ 01:59, ...
        query_length: int
        distance_function: str
        number_of_motifs: int
        lower_limit_of_the_number_of_single_motif: int
    output:
        output_json_file: str
            keys = matrix_profile, matrix_profile_index, motif_index, discord_index
"""



import json
import csv
import datetime as dt
import operator
import numpy as np
import random
import requests
from operator import itemgetter
import time
import sys
import platform

from get_clean_data import get_clean_data



def distance_profile_preprocessing(data, query_length):
    
    data_length = len(data)
    
    data[len(data) : 2 * len(data)] = [0] * len(data)
    
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



def distance_profile_mass(query, query_index, data_freq, data_length, data_sum2, data_sum, data_mean,  \
                    data_sigma2, data_sigma, exclusion_zone):
    
    query_length = len(query)
    
    # normalize the query
    query = np.divide(np.subtract(query, np.mean(query)), np.std(query))
    
    query = query.tolist()
    
    #reverse the query
    query = query[::-1]

    # append zeros
    query[query_length : 2 * data_length] = [0] * (2 * data_length - query_length)
    
    query_freq = np.fft.fft(query)
    dataquery = np.fft.ifft(np.multiply(data_freq, query_freq))

    query_sum = np.sum(query)
    query_sum2 = np.sum(np.power(query, 2))

    distance_profile = np.divide((data_sum2 - 2 * np.multiply(data_sum, data_mean) \
                       + query_length * np.power(data_mean, 2)), data_sigma2)     \
                       - np.divide(2 * dataquery[query_length - 1 : data_length]   \
                       - np.multiply(query_sum, data_mean), data_sigma) + query_sum2
    distance_profile = np.abs(np.sqrt(distance_profile))
    
    distance_profile = distance_profile.tolist()
    
    
    distance_profile = distance_profile_exclusionzone(distance_profile, data_length, query_index, query_length, exclusion_zone)

    return distance_profile



def distance_profile_ed(data, query_index, query_length, exclusion_zone):
    
    query = data[query_index : query_index + query_length]
    
    distance_profile = []

    for i in range(len(data) - query_length + 1):
        distance_profile.append(np.linalg.norm(map(operator.sub, query, data[i : i + query_length])))
    
    
    distance_profile = distance_profile_exclusionzone(distance_profile, len(data), query_index, query_length, exclusion_zone)
    
    return distance_profile



def distance_profile_dtw(data, query_index, query_length, exclusion_zone):
    
    query = data[query_index : query_index + query_length]
    
    distance_profile = []

    for index in range(len(data) - query_length + 1):
        dtw_matrix = []
        
        for i in range(query_length + 1):
            dtw_matrix.append([float("Inf")] * (query_length + 1))
        
        dtw_matrix[0][0] = 0
        
        for i in range(1, query_length + 1):
            for j in range(1, query_length + 1):
                cost = abs(query[i-1] - data[index : index + query_length][j-1])
                dtw_matrix[i][j] = cost + min(dtw_matrix[i-1][j], dtw_matrix[i][j-1], dtw_matrix[i-1][j-1])
        
        distance_profile.append(dtw_matrix[query_length][query_length])
    
    
    distance_profile = distance_profile_exclusionzone(distance_profile, len(data), query_index, query_length, exclusion_zone)
    
    return distance_profile



def distance_profile_exclusionzone(distance_profile, data_length, query_index, query_length, exclusion_zone):    
    
    start = max(0, query_index - exclusion_zone)
    end = min(data_length - query_length + 1, query_index + exclusion_zone + 1)
    distance_profile[start : end] = [float("Inf")] * (end - start)
    
    return distance_profile


    
def update_matrix_profile(distance_profile, matrix_profile, matrix_profile_index, data_length, query_length, query_index):
    
    for i in range(data_length - query_length + 1):
        if distance_profile[i] < matrix_profile[i]:
            matrix_profile[i] = distance_profile[i]
            matrix_profile_index[i] = query_index
     
                           
                                
def find_motif_and_discord(data, query_length, exclusion_zone, distance_function, matrix_profile, matrix_profile_index, number_of_motifs, lower_limit_of_the_number_of_single_motif):
    
    # find motif
    
    matrix_profile_and_index_sort = []
    for i in range(len(matrix_profile)):
        matrix_profile_and_index_sort.append({})
        matrix_profile_and_index_sort[i]["neighbor_distance"] = matrix_profile[i]
        matrix_profile_and_index_sort[i]["neighbor_index"] = matrix_profile_index[i]
        matrix_profile_and_index_sort[i]["query_index"] = i
        
    matrix_profile_and_index_sort = sorted(matrix_profile_and_index_sort, key = operator.itemgetter("neighbor_distance"), reverse = False)
    
    radius = 2
    motif_index = []
    i = 0           # index of number_of_motifs
    step = 1        # step = 1 : find the smallest matrix profile
                    # step = 2 : find the neighbors
                    # step = 3 : check lower_limit_of_the_number_of_single_motif
    while i < number_of_motifs:
        
        # find the smallest matrix profile
        
        if step == 1:
            
            legal = True
            
            step_1_motif_candidate = matrix_profile_and_index_sort[0]["query_index"]
            step_1_motif_candidate_correspond = matrix_profile_and_index_sort[0]["neighbor_index"]
            
            matrix_profile_and_index_sort.remove(matrix_profile_and_index_sort[0])
            
            # check existence
            for element_1 in motif_index:
                for element_2 in element_1:
                    if step_1_motif_candidate == element_2 or step_1_motif_candidate_correspond == element_2:
                        legal = False
                
            if legal == True:      
                motif_index.append([])
                motif_index[i].append(step_1_motif_candidate)
                motif_index[i].append(step_1_motif_candidate_correspond)
                
                step = 2
        
        
        # find the neighbors 
        
        if step == 2:
            
            for j in range(2):      # j = 0 : step_1_motif_candidate
                                    # j = 1 : step_1_motif_candidate_correspond
            
                if distance_function == "mass":
                    # distanceprofile_preprocessing
                    data_for_function = data[:]
                    data_freq, data_sum2, data_sum, data_mean, data_sigma2, data_sigma = distance_profile_preprocessing(data_for_function, query_length)
                    
                if distance_function == "mass":
                    distance_profile = distance_profile_mass(data[motif_index[i][j] : motif_index[i][j] + query_length], motif_index[i][j], data_freq, \
                                                              len(data), data_sum2, data_sum, data_mean, data_sigma2, data_sigma, exclusion_zone)
                elif distance_function == "ed":
                    distance_profile = distance_profile_ed(data, motif_index[i][j], query_length, exclusion_zone)
                
                elif distance_function =="dtw":
                    distance_profile = distance_profile_dtw(data, motif_index[i][j], query_length, exclusion_zone)
                
                for index in range(len(distance_profile)):
                    
                    legal = True
                    
                    if distance_profile[index] <= radius * matrix_profile[motif_index[i][j]]:
                        # check existence
                        for element_1 in motif_index:
                            for element_2 in element_1:
                                if index == element_2:
                                    legal = False
                        
                        # check exclusion_zone between neighbors
                        for element in motif_index[i]:
                            if abs(element - index) < exclusion_zone:
                                legal = False
                                if index in [element["query_index"] for element in matrix_profile_and_index_sort if element["query_index"] == index]:
                                    matrix_profile_and_index_sort.remove(next(element for element in matrix_profile_and_index_sort if element["query_index"] == index))
                    
                        if legal == True:
                            if index in [element["query_index"] for element in matrix_profile_and_index_sort if element["query_index"] == index]: 
                                motif_index[i].append(index)
                                matrix_profile_and_index_sort.remove(next(element for element in matrix_profile_and_index_sort if element["query_index"] == index))
            
            step = 3
        
        
        # check lower_limit_of_the_number_of_single_motif
        
        if step == 3:
            
            if len(motif_index[i]) < lower_limit_of_the_number_of_single_motif:
                if radius < 10: 
                    radius = radius + 1
                    step = 2
                else:
                    if number_of_motifs > lower_limit_of_the_number_of_single_motif * 5:
                        break
                    else:
                        number_of_motifs += 1
                        radius = 2
                        i += 1
                        step = 1
            else:
                radius = 2
                i += 1
                step = 1
            
    
    # remove the extra motifs (length is lower than lower_limit_of_the_number_of_single_motif)
    
    motif_index = [element for element in motif_index if not len(element) < lower_limit_of_the_number_of_single_motif]
    
    
    # sort motif
    
    for i in range(len(motif_index)):
        motif_index[i] = sorted(motif_index[i])
    
    
    # find discord
    
    matrix_profile_and_index_sort = []
    for i in range(len(matrix_profile)):
        matrix_profile_and_index_sort.append([])
        matrix_profile_and_index_sort[i].append(matrix_profile[i])
        matrix_profile_and_index_sort[i].append(matrix_profile_index[i])

    matrix_profile_and_index_sort.sort(key = operator.itemgetter(0), reverse = False)
    
    discord_index = []
    i = 0
    while i < number_of_motifs:
        legal = True
        
        discord_candidate = matrix_profile_and_index_sort[len(matrix_profile_and_index_sort) - 1][1]
        matrix_profile_and_index_sort.remove(matrix_profile_and_index_sort[len(matrix_profile_and_index_sort) - 1])
        
        if discord_candidate == -1:
            legal = False

        if legal == True:      
            discord_index.append(discord_candidate)
            
            i = i + 1
    
    
    return motif_index, discord_index
    
    
def compute_matrix_profile(data, query_length, distance_function, number_of_motifs, lower_limit_of_the_number_of_single_motif):
    
    # set data_for_function
    
    data_for_function = data[:]
    
    
    # check data
    
    if len(data_for_function) == 0:
        print("no data for matrix profile")
        sys.exit()
    
    
    # check input
    
    if query_length > len(data_for_function) / 20:
        print("Illegal query_length: too long")
        sys.exit()
    elif query_length < 4:
        print("Illegal query_length: too short")
        sys.exit()
    
    if distance_function != "mass" and distance_function != "ed" and distance_function != "dtw":
        print("Illegal distance_function")
        sys.exit()
    
    
    # need to do some preprocessing if distance function is mass
    
    if distance_function == "mass":
        data_for_function = data[:]
        data_freq, data_sum2, data_sum, data_mean, data_sigma2, data_sigma = \
        distance_profile_preprocessing(data_for_function, query_length)
    
    
    # compute distance_profile for all index
    
    distance_profile = []
    
    exclusion_zone = int(round(query_length / 2.0))
    data_for_function = data[:]
    percentage = 0
    
    for i in range(len(data_for_function) - query_length + 1):
        
        # show the percentage of the progress
        
        if platform.system() == "Windows":
            if (i / (len(data_for_function) - query_length + 1)) * 100 > percentage:
                percentage += 10
                print(str(percentage) + " %")
        
        
        # compute distance_profile
        
        if distance_function == "mass":
            distance_profile.append(distance_profile_mass(data_for_function[i : i + query_length], i, data_freq, \
                                                    len(data_for_function), data_sum2, data_sum, \
                                                    data_mean, data_sigma2, data_sigma, exclusion_zone))
        elif distance_function == "ed":
            distance_profile.append(distance_profile_ed(data_for_function, i, query_length, exclusion_zone))
            
        elif distance_function =="dtw":
            distance_profile.append(distance_profile_dtw(data_for_function, i, query_length, exclusion_zone))

    
    # update matrix_profile in random order
    
    data_for_function = data[:]
    random_number_for_choose_index_of_distance_profile = list(range(0, len(data_for_function) - query_length + 1))
    random.shuffle(random_number_for_choose_index_of_distance_profile)
 
    matrix_profile = [float("Inf")] * (len(data_for_function) - query_length + 1)
    matrix_profile_index = [-1] * (len(data_for_function) - query_length + 1)
  
    for i in random_number_for_choose_index_of_distance_profile:
        update_matrix_profile(distance_profile[i], matrix_profile, matrix_profile_index, \
                            len(data_for_function), query_length, i)    

    
    # find motif and discord
    
    motif_index, discord_index = find_motif_and_discord(data_for_function, query_length, exclusion_zone, distance_function, \
                                                        matrix_profile, matrix_profile_index, number_of_motifs, lower_limit_of_the_number_of_single_motif)
    
    
    return matrix_profile, matrix_profile_index, motif_index, discord_index

def compute_matrix_profile_web(device_id, start_date, end_date, sample_rate, days, hours, query_length, distance_function, number_of_motifs, lower_limit_of_the_number_of_single_motif):
    
    # deal with days and hour
    
    if days == []:
        days = list(range(0, 7))
    if hours == []:
        hours = list(range(0, 24))
       
    
    # get data
    
    data = get_clean_data(device_id, start_date, end_date, sample_rate, days, hours)
    
    
    # we choose the pm25 data (also get other data to return)
    
    timestamp = []
    pm25 = []
    temperature = []
    humidity = []
    
    for record in data:
        timestamp.append(str(record["timestamp"]))
        pm25.append(record["pm25"])
        temperature.append(record["temperature"])
        humidity.append(record["humidity"])
    
    
    # call function
    
    data = pm25
    
    matrix_profile, matrix_profile_index, motif_index, discord_index = compute_matrix_profile(data, query_length, distance_function, \
                                                                                              number_of_motifs, lower_limit_of_the_number_of_single_motif)
    
    
    # deal with "infinity" value
    
    for i in range(len(matrix_profile)):
        if matrix_profile[i] == float("Inf"):
            matrix_profile[i] = "infinity"
    
    
    # return as json file
    
    output_json_file = json.dumps({'matrix_profile' : matrix_profile , 'matrix_profile_index' : matrix_profile_index ,\
                                   'motif_index' : motif_index , 'discord_index' : discord_index, \
                                   'timestamp' : timestamp , 'pm25' : pm25, \
                                   'temperature' : temperature , 'humidity' : humidity})
    
    
    return output_json_file



if __name__ == "__main__":
    
    # initial start_time for calculating spending time
    
    start_time = time.time()
    
    
    
    # we choose the pm25 data (also get other data to plot)
    
    timestamp = []
    with open('data/07/07-timestamp.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            timestamp.append(row[0])
    
    pm25 = []
    with open('data/07/07-pm25.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            pm25.append(int(row[0]))
    
    temperature = []
    with open('data/07/07-temperature.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            temperature.append(int(row[0]))
    
    humidity = []
    with open('data/07/07-humidity.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            humidity.append(int(row[0]))
    
    
    # call function
    
    data = pm25
    query_length = [12, 24, 36, 48, 60, 72, 144, 288]
    distance_function = "mass"
    number_of_motifs = 3
    lower_limit_of_the_number_of_single_motif = 3
    
    for single_query_length in query_length:
    
        matrix_profile, matrix_profile_index, motif_index, discord_index = compute_matrix_profile(data, single_query_length, distance_function, \
                                                                                          number_of_motifs, lower_limit_of_the_number_of_single_motif)
        
        
        
        # save as csv file
        '''
        with open('06-full_data.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["matrix_profile", "matrix_profile_index", "motif_index", "discord_index"])
            for i in data:
                writer.writerow(record)
        '''
        with open("data/07/mp/" + str(single_query_length) + "/07-matrix_profile.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for element in matrix_profile:
                writer.writerow([element])
                
        with open("data/07/mp/" + str(single_query_length) + "/07-matrix_profile_index.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for element in matrix_profile_index:
                writer.writerow([element])
            
        with open("data/07/mp/" + str(single_query_length) + "/07-motif_index.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for element in motif_index:
                writer.writerow([element])
                
        with open("data/07/mp/" + str(single_query_length) + "/07-discord_index.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for element in discord_index:
                writer.writerow([element])
    
    '''
    # plot (only Windows)
    
    if platform.system() == "Windows":
        
        import matplotlib.pyplot as plt
        
        print("################   matrix profile   ################")
        
        for i in range(number_of_motifs):
            print("--------------------------------------------------------------")
            print("motif (k = " + str(i + 1) + "):")
            for element in motif_index[i]:
                plt.plot(pm25[element : element + query_length])
            plt.show()
            
            for element in motif_index[i]:
                print("timestamp : " + timestamp[element])
            
            print("\n\ncorresponding temperature:")
            for element in motif_index[i]:
                plt.plot(temperature[element : element + query_length])
            plt.show()
            
            print("\n\ncorresponding humidity:")
            for element in motif_index[i]:
                plt.plot(humidity[element : element + query_length])
            plt.show()
        
                    
        for i in range(number_of_motifs):
            print("--------------------------------------------------------------")
            print("discord (k = " + str(i + 1) + "):")
            plt.plot(pm25[discord_index[i] : discord_index[i] + query_length])
            plt.show()         
            print("timestamp : " + timestamp[discord_index[i]])
            
            print("\n\ncorresponding temperature:")
            plt.plot(temperature[discord_index[i] : discord_index[i] + query_length])
            plt.show()
            
            print("\n\ncorresponding humidity:")
            plt.plot(humidity[discord_index[i] : discord_index[i] + query_length])
            plt.show()
    '''
    
    # show spending time
    
    print("spending time: %s seconds" % (time.time() - start_time))
