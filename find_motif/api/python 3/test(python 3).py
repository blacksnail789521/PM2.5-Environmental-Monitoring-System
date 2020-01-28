'''
import json
import csv
import datetime as dt
from operator import itemgetter
import numpy as np
import random
from pprint import pprint

import matplotlib.pyplot as plt

'''

'''

from joblib import Parallel, delayed
import multiprocessing
import time
# what are your inputs, and what operation do you want to
# perform on each input. For example...



def processInput(i):
    return i * i


if __name__ == '__main__':
    
    start_time = time.time()
    
    r = 1000000
    
    results = list()
    inputs = range(r)
    for i in inputs:
        results.append(processInput(i))
    #print(results)
    mid_time = time.time()
    print("serial time: ", mid_time - start_time)
    
    
    results = list()
    inputs = range(r)
    num_cores = multiprocessing.cpu_count()
    print(num_cores)
    results = Parallel(n_jobs=8)(delayed(processInput)(i) for i in inputs)
    #print(results)
    end_time = time.time()
    print("parallel time: ", end_time - mid_time)
'''


import numpy as np
from matplotlib.path import Path
from joblib import Parallel, delayed
import time
import sys

## Check if one line segment contains another. 

def check_paths(path):
    for other_path in a:
        res='no cross'
        chck = Path(other_path)
        if chck.contains_path(path)==1:
            res= 'cross'
            break
    return res

if __name__ == '__main__':
    ## Create pairs of points for line segments
    a = zip(np.random.rand(5000,2),np.random.rand(5000,2))
    b = zip(np.random.rand(300,2),np.random.rand(300,2))

    now = time.time()
    if len(sys.argv) >= 2:
        res = Parallel(n_jobs=int(sys.argv[1])) (delayed(check_paths) (Path(points)) for points in b)
    else:
        res = [check_paths(Path(points)) for points in b]
    print("Finished in", time.time()-now , "sec")