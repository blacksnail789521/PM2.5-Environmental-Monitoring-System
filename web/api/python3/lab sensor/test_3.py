import csv
import matplotlib.pyplot as plt
import numpy as np

pm25 = []
with open('data/MP_first_test_penguin_sample.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        pm25.append(float(row[0]))

plt.plot(pm25)
plt.show()


motif_index = []
i = 0
with open("data/motif_index.csv", 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        motif_index.append([])
        tmp = row[0]
        tmp = tmp.replace("[", "").replace("]", "").split(", ")
        for element in tmp:
            motif_index[i].append(int(element))
        i += 1


for i in range(3):
    print("--------------------------------------------------------------")
    print("motif (k = " + str(i + 1) + "):")
    for element in motif_index[i]:
        plt.plot(pm25[element : element + 800])
    plt.show()