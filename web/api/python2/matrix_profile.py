import json
import datetime as dt
import operator
import numpy as np
import random
import requests
from operator import itemgetter
from pprint import pprint


            




def daily_data_preprocessing(device_id, date, sample_rate):
    
    # web crawler
    
    res = requests.get("https://pm25.lass-net.org/data/history-date.php?device_id=" + device_id + "&date=" + date)
    
    input_json_file = {}
    if not res.json()['feeds']:
        # no data
        #print date + " : no data"
        return "no data"
    
    if 'AirBox' in res.json()['feeds'][0]:
        input_json_file = res.json()['feeds'][0]["AirBox"]
    elif 'LASS' in res.json()['feeds'][0]:
        input_json_file = res.json()['feeds'][0]["AirBox"]
    
    
    
    # get timestamp, pm25, temperature, humidity
    
    data = []
    
    i = 0
    for record in input_json_file:
        data.append([])
        data[i].append(dt.datetime.strptime(record, "%Y-%m-%dT%H:%M:%SZ"))
        data[i].append(int(input_json_file[record]["s_d0"]))
        data[i].append(int(input_json_file[record]["s_t0"]))
        data[i].append(int(input_json_file[record]["s_h0"]))
        i = i + 1
    
    
    
    # sort with timestamp
    
    data.sort(key = itemgetter(0), reverse = False)
    
    
    
    # align head of timestamp (start at 00:00:00) and fill the missing items (copy the first value)
    
    final_data = []
    buf = []
    start = dt.datetime.strptime(date + " 00:00:00", "%Y-%m-%d %H:%M:%S")
    
    delta_int = sample_rate
    delta = dt.timedelta(minutes = delta_int)
    slidewindow = start
    
    
    i = 0   #data index
    j = 0   #final_data index
    k = 0   #buffer index
    
    while slidewindow < data[0][0]:
        final_data.append([])
        final_data[j].append(slidewindow)
        final_data[j].append(data[0][1])
        final_data[j].append(data[0][2])
        final_data[j].append(data[0][3])
        j = j + 1
        slidewindow = slidewindow + delta
    
    
    # fill the missing items of the original data (copy the previous value)
    
    while 1:
        if i == len(data):
            final_data.append([])
            final_data[j].append(slidewindow)
            final_data[j].append(int(np.mean(buf, axis = 0)[0]))
            final_data[j].append(int(np.mean(buf, axis = 0)[1]))
            final_data[j].append(int(np.mean(buf, axis = 0)[2]))
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
                final_data[j].append(int(np.mean(buf, axis = 0)[0]))
                final_data[j].append(int(np.mean(buf, axis = 0)[1]))
                final_data[j].append(int(np.mean(buf, axis = 0)[2]))
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
    
    
    
    # align tail of timestamp (ex: end at 23:55:00) and fill the missing items (copy the last value)
    
    final_data_end_timestamp = dt.datetime.strptime(date + " 23:"+ str( 60 - (delta_int if 1440 % delta_int == 0 else 1440 - (1440/delta_int)*delta_int) ) + ":00", "%Y-%m-%d %H:%M:%S")
    
    while final_data[len(final_data) - 1][0] < final_data_end_timestamp:
        slidewindow = slidewindow + delta
        final_data.append([])
        final_data[len(final_data) - 1].append(slidewindow)
        final_data[len(final_data) - 1].append(final_data[len(final_data) - 2][1])
        final_data[len(final_data) - 1].append(final_data[len(final_data) - 2][2])
        final_data[len(final_data) - 1].append(final_data[len(final_data) - 2][3])
    
    
    return final_data



def data_preprocessing(device_id, start_date, end_date, sample_rate):
    
    delta = dt.timedelta(days = 1)
    
    start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")
    current_date = start_date
    
    data = []
    while current_date <= end_date:
        #print str(current_date).split(" ")[0]
        if not daily_data_preprocessing(device_id, str(current_date).split(" ")[0], sample_rate) == "no data":
            data.append( daily_data_preprocessing(device_id, str(current_date).split(" ")[0], sample_rate) )
        current_date = current_date + delta

    return data




            
########## matrix_profile ######################################################          
            
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
    
    radius = 2
    # find motif
    
    matrix_profile_and_index_sort = []
    for i in range(len(matrix_profile)):
        matrix_profile_and_index_sort.append([])
        matrix_profile_and_index_sort[i].append(matrix_profile[i])
        matrix_profile_and_index_sort[i].append(matrix_profile_index[i])

    matrix_profile_and_index_sort.sort(key = operator.itemgetter(0), reverse = False)
    
    motif_index = []
    i = 0
    while i < number_of_motifs:
        step = 1       # step = 1 : find the smallest matrix profile
                       # step = 2 : find the neighbors
                       # step = 3 : check lower_limit_of_the_number_of_single_motif
                       
        legel = True
        
        # find the smallest matrix profile
        if step == 1:
            
            step_1_motif_candidate = matrix_profile_and_index_sort[0][1]
            step_1_motif_candidate_correspond = matrix_profile_index[matrix_profile_and_index_sort[0][1]]
            matrix_profile_and_index_sort.remove(matrix_profile_and_index_sort[0])
            
            # check existence
            for element_1 in motif_index:
                for element_2 in element_1:
                    if step_1_motif_candidate == element_2 or step_1_motif_candidate_correspond == element_2:
                        legel = False
                
            if legel == True:      
                motif_index.append([])
                motif_index[i].append(step_1_motif_candidate)
                motif_index[i].append(step_1_motif_candidate_correspond)
                
                step = 2
        
        
        # find the neighbors    
        if step == 2:
            
            if distance_function == "mass":
                # distanceprofile_preprocessing
                data_function = data[:]
                data_freq, data_sum2, data_sum, data_mean, data_sigma2, data_sigma = distance_profile_preprocessing(data_function, query_length)
                
            if distance_function == "mass":
                distance_profile_1 = distance_profile_mass(data[motif_index[i][0] : motif_index[i][0] + query_length], motif_index[i][0], data_freq, \
                                                          len(data), data_sum2, data_sum, data_mean, data_sigma2, data_sigma, exclusion_zone)
            elif distance_function == "ed":
                distance_profile_1 = distance_profile_ed(data, motif_index[i][0], query_length, exclusion_zone)
            
            elif distance_function =="dtw":
                distance_profile_1 = distance_profile_dtw(data, motif_index[i][0], query_length, exclusion_zone)
            
            for index in range(len(distance_profile_1)):
                if distance_profile_1[index] <= radius * matrix_profile[motif_index[i][0]] or distance_profile_1[index] <= radius * matrix_profile[motif_index[i][1]]:
                    # check existence
                    for element_1 in motif_index:
                        for element_2 in element_1:
                            if index == element_2:
                                legel = False
                
                    if legel == True:      
                        motif_index[i].append(index)
            
            if distance_function == "mass":
                distance_profile_2 = distance_profile_mass(data[motif_index[i][1] : motif_index[i][1] + query_length], motif_index[i][1], data_freq, \
                                                          len(data), data_sum2, data_sum, data_mean, data_sigma2, data_sigma, exclusion_zone)
            elif distance_function == "ed":
                distance_profile_2 = distance_profile_ed(data, motif_index[i][1], query_length, exclusion_zone)
            
            elif distance_function =="dtw":
                distance_profile_2 = distance_profile_dtw(data, motif_index[i][1], query_length, exclusion_zone)
            
            for index in range(len(distance_profile_2)):
                if distance_profile_2[index] <= radius * matrix_profile[motif_index[i][0]] or distance_profile_2[index] <= radius * matrix_profile[motif_index[i][1]]:
                    # check existence
                    for element_1 in motif_index:
                        for element_2 in element_1:
                            if index == element_2:
                                legel = False
                
                    if legel == True:      
                        motif_index[i].append(index)
            
            step = 3
        
        
        # check lower_limit_of_the_number_of_single_motif
        if step == 3:
            
            if len(motif_index[i]) < lower_limit_of_the_number_of_single_motif: 
                radius = radius + 1
            else:
                i = i + 1
            
            step = 1
    
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
        legel = True
        
        discord_candidate = matrix_profile_and_index_sort[len(matrix_profile_and_index_sort) - 1][1]
        matrix_profile_and_index_sort.remove(matrix_profile_and_index_sort[len(matrix_profile_and_index_sort) - 1])
        
        if discord_candidate == -1:
            legel = False

        if legel == True:      
            discord_index.append(discord_candidate)
            
            i = i + 1
    
    
    return motif_index, discord_index
    
    
def matrix_profile(device_id, start_date, end_date, sample_rate, query_length, time_mode, distance_function, number_of_motifs, lower_limit_of_the_number_of_single_motif):
    
    # get data
    
    data = data_preprocessing(device_id, start_date, end_date, sample_rate)
    
    timestamp = []
    pm25 = []
    tempature = []
    humidity = []
    
    for daily_data in data:
        for i in range(len(daily_data)):
            timestamp.append(str(daily_data[i][0]))
            pm25.append(daily_data[i][1])
            tempature.append(daily_data[i][2])
            humidity.append(daily_data[i][3])
    
    data_for_compute_motif = pm25
    
    
    # check data
    
    if len(data_for_compute_motif) == 0:
        return "no data for matrix profile"
    
    
    # check input
    
    if query_length > len(data_for_compute_motif) / 20 or query_length < 4:
        #print "Illegal query_length"
        return "Illegal query_length"
    
    if distance_function != "mass" and distance_function != "ed" and distance_function != "dtw":
        #print "Illegal distance_function"
        return "Illegal distance_function"
    
    
    
    if distance_function == "mass":
        data_function = data_for_compute_motif[:]
        data_freq, data_sum2, data_sum, data_mean, data_sigma2, data_sigma = \
        distance_profile_preprocessing(data_function, query_length)
       
    distance_profile = []
    
    exclusion_zone = int(round(query_length / 2.0))
    
    for i in range(len(data_for_compute_motif) - query_length + 1):
        if distance_function == "mass":
            distance_profile.append(distance_profile_mass(data_for_compute_motif[i : i + query_length], i, data_freq, \
                                                    len(data_for_compute_motif), data_sum2, data_sum, \
                                                    data_mean, data_sigma2, data_sigma, exclusion_zone))
        elif distance_function == "ed":
            distance_profile.append(distance_profile_ed(data_for_compute_motif, i, query_length, exclusion_zone))
            
        elif distance_function =="dtw":
            distance_profile.append(distance_profile_dtw(data_for_compute_motif, i, query_length, exclusion_zone))

    
    random_array = range(0, len(data_for_compute_motif) - query_length + 1)
    random.shuffle(random_array)
 
    matrix_profile = [float("Inf")] * (len(data_for_compute_motif) - query_length + 1)
    matrix_profile_index = [-1] * (len(data_for_compute_motif) - query_length + 1)
  
    for i in random_array:
        update_matrix_profile(distance_profile[i], matrix_profile, matrix_profile_index, \
                            len(data_for_compute_motif), query_length, i)    

    
    motif_index, discord_index = find_motif_and_discord(data_for_compute_motif, query_length, exclusion_zone, distance_function, \
                                                        matrix_profile, matrix_profile_index, number_of_motifs, lower_limit_of_the_number_of_single_motif)
    
 
    
    # deal with "infinity" value
    for i in range(len(matrix_profile)):
        if matrix_profile[i] == float("Inf"):
            matrix_profile[i] = "infinity"
    
    return json.dumps({'timestamp' : timestamp ,\
                        'pm25' : pm25,\
                        'tempature' : tempature,\
                        'humidity' : humidity,\
                        'matrix_profile' : matrix_profile ,\
                        'matrix_profile_index' : matrix_profile_index ,\
                        'motif_index' : motif_index ,\
                        'discord_index' : discord_index})
    
    
    #return timestamp, pm25, tempature, humidity, matrix_profile, matrix_profile_index, motif_index, discord_index


#data = data_preprocessing("74DA3895C2F0", "2017-05-10", "2017-05-14", 5)
#pprint(matrix_profile("74DA38B05346", "2017-05-10", "2017-05-10", 5, 12, "days", "mass", 3, 2))
#pprint(motif_index)
