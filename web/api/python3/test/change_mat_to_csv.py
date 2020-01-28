import scipy.io
import numpy as np
data = scipy.io.loadmat("MP_first_test_penguin_sample.mat")

for i in data:
    if '__' not in i and 'readme' not in i:
        np.savetxt(("MP_first_test_penguin_sample.csv"),data[i],delimiter=',')