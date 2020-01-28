import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint
import time
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
import multiprocessing



data = [1, 2, 3, 4, 5]

new_data_point = 6

new_data = data[:]
new_data.append(new_data_point)

query_length = 3

pprint(new_data[len(new_data) - query_length : len(new_data)])

new_query_index = len(new_data) - query_length
pprint(new_query_index)