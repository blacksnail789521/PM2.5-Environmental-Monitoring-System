from joblib import Parallel, delayed
import multiprocessing
import time

def processInput(i):
    return i * i

if __name__ == '__main__':
    
    start_time = time.time()
    
    r = 100000
    
    results = list()
    inputs = range(r)
    
    num_cores = multiprocessing.cpu_count()
    results = Parallel(n_jobs = num_cores)(delayed(processInput)(i) for i in inputs)
    #results = Parallel(n_jobs = num_cores, backend="threading")(delayed(processInput)(i) for i in inputs)
    
    end_time = time.time()
    print("parallel time: ", end_time - start_time)
