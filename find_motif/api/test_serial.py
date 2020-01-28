import time


def processInput(i):
    return i * i


if __name__ == '__main__':
    
    start_time = time.time()
    
    r = 100000
    
    results = list()
    inputs = range(r)
    
    for i in inputs:
        results.append(processInput(i))
    
    end_time = time.time()
    print("serial time: ", end_time - start_time)