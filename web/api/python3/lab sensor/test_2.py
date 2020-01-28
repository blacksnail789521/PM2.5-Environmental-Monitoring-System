import csv
import matplotlib.pyplot as plt
from datetime import datetime

query_length = 288


timestamp = []
with open('data/07/07-timestamp.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        timestamp.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))

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


motif_index = []
i = 0
with open("data/07/mp/3/"+ str(query_length) + "/07-motif_index.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        motif_index.append([])
        tmp = row[0]
        tmp = tmp.replace("[", "").replace("]", "").split(", ")
        for element in tmp:
            motif_index[i].append(int(element))
        i += 1
    
plt.plot(timestamp, pm25)
plt.show()



for i in range(1):
    print("--------------------------------------------------------------")
    print("motif (k = " + str(i + 1) + "):")
    for element in motif_index[i]:
        plt.plot(pm25[element : element + query_length])
    plt.show()
    '''
    for element in motif_index[i]:
        print("timestamp : " + str(timestamp[element]))
    '''
    print("\n\ncorresponding temperature:")
    for element in motif_index[i]:
        plt.plot(temperature[element : element + query_length])
    plt.show()
    
    print("\n\ncorresponding humidity:")
    for element in motif_index[i]:
        plt.plot(humidity[element : element + query_length])
    plt.show()