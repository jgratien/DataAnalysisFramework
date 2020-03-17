import numpy as np
import matplotlib.pyplot as plt
import time


def init_spark(app_name):
    import findspark
    findspark.init()
    import pyspark
    from pyspark import SparkContext, SparkConf

    sc_conf = SparkConf()
    sc_conf.setAppName(app_name)
    sc_conf.setMaster('local[*]')
    sc_conf.set('spark.executor.memory', '4g')
    sc_conf.set('spark.executor.cores', '4')
    sc_conf.set('spark.driver.memory', '32G')
    sc_conf.set('spark.cores.max', '32')
    sc_conf.set('spark.driver.maxResultSize', '10G')
    sc_conf.set('spark.logConf', True)
    sc_conf.getAll()
    sc = None
    try:
        sc.stop()
        sc = SparkContext(conf=sc_conf)
    except:
        sc = SparkContext(conf=sc_conf)
    return sc


def createIMGBinaryFile(filename,nx,ny,nz):
    import numpy as np
    t0 = time.process_time()
    with open(filename, mode='wb') as file:
        for k in range(nz):
            np.random.seed(k)
            layer = np.random.randint(0, 255, (nx,ny),dtype=np.uint8)
            file.write(layer.tobytes())
            
    t1 = time.process_time()
    print("TIME TO WRITE BINARY FILE",t1-t0)

def readIMGBinaryFile(filename,nx,ny,nz,layer_pack_size=1) :
    import numpy as np
    layer_nb_bytes = nx*ny
    t0 = time.process_time()
    with open(filename,"rb") as f:
        nb_layer_pack = nz//layer_pack_size
        print("LAYER PACK SIZE:",layer_pack_size)
        print("NB LAYER PACK",nb_layer_pack)
        for p in range(nb_layer_pack):
            # READ 
            layer_bytes = f.read(layer_nb_bytes*layer_pack_size)
            layer = np.frombuffer(layer_bytes,dtype=np.uint8)
    t1 = time.process_time()
    print("TIME TO READ BINARY FILE",t1-t0)
    
def main():
    #
    # CREATE BINARY IMAGE OF SIZE NX x NY X NZ then save to binary file
    #
    nx=1000
    ny=1000
    nz=1000
    filename="IMG-"+str(nx)+"x"+str(ny)+"x"+str(nz)+".bin"
    createIMGBinaryFile(filename,nx,ny,nz)
    
    #
    # READ BINARY IMAGE OF SIZE NX x NY X NZ by LAYER
    #
    readIMGBinaryFile(filename,nx,ny,nz)
    
    
    #
    # READ BINARY IMAGE OF SIZE NX x NY X NZ by LAYER PACK OF SIZE 10
    #
    readIMGBinaryFile(filename,nx,ny,nz,10)

if __name__ == '__main__':
    main()
