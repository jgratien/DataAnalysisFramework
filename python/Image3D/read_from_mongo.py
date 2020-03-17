from Image.ImageIO import ImageIO
import time
import numpy as np 

def read_from_mongo(name):
    # Se connecter au serveur
    imageIO = ImageIO()
    t0 = time.process_time()
    img=imageIO.header_img.find_one({"name":name})
    t1=time.process_time()-t0
    print('TIME TO FIND IMG IN mongoDB',t1)
    nx=img['x']
    ny=img['y']
    nz=img['z']
    print('SHAPE', nx, ny, nz)
    t0 = time.process_time()
    data_file = imageIO.fs.find_one({"_id":img['cube_id']})
    bytes_data = data_file.read()
   # print('NB BYTES', bytes_data.__len__(),np.dtype('uint8').itemsize)
    array_data = np.frombuffer(bytes_data)      # dtype='uint8', count=int(bytes_data.__len__()/np.dtype('uint8').itemsize))
    t1=time.process_time()-t0
    print('TIME TO LOAD IMG DATA FROM mongoDB', t1)
    array3D_data = np.reshape(array_data,(nx, ny, nz))
    print('SHAPE2 :', array3D_data.shape)
    return array3D_data

data = read_from_mongo('cube_test_size100_8')

