import time
import numpy as np
t0 = time.process_time()
with open("binary_file2", mode='rb') as file:
    bytes_data = file.read()
    array_data = np.frombuffer(bytes_data, dtype='b', count=bytes_data.__len__())
t1=time.process_time()-t0
print("Local FS READING TIME : ",t1)
print('NB PIXELS :',len(array_data))

