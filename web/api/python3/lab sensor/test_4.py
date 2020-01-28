import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pm25 = []
with open('data/07/07-pm25.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        pm25.append(int(row[0]))

timestamp = []
with open('data/07/07-timestamp.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        timestamp.append(row[0].split(" ")[0])

plt.plot(pm25)
plt.show()


pm25_n = np.divide(np.subtract(pm25, np.mean(pm25)), np.std(pm25))

plt.plot(pm25_n)
plt.show()


from statsmodels.tsa.seasonal import seasonal_decompose

df = pd.DataFrame(pm25)
df.index = pd.DatetimeIndex(freq = "w", start = 0, periods = 8928)
#print(df)

result = seasonal_decompose(df, model='additive')
#result = seasonal_decompose(df, model='multiplicative')

print("--------------------------------------------------------------")
print("observed")
plt.plot(result.observed[0].tolist())
plt.show()

print("--------------------------------------------------------------")
print("trend")
plt.plot(result.trend[0].tolist())
plt.show()

print("--------------------------------------------------------------")
print("seasonal")
plt.plot(result.seasonal[0].tolist()[:288])
plt.show()

print("--------------------------------------------------------------")
print("resid")
plt.plot(result.resid[0].tolist())
plt.show()