import findspark
findspark.init()
import pyspark
from pyspark import SparkContext, SparkConf
import numpy as np
import matplotlib.pyplot as plt
from median_vspark3D import image_partition3D, get_neighbors3D, median_filter_3D, sorted_neighbors, gaussian_noise
import time


def create_dummy():
    s = np.random.normal(128, 5, 100)
    img_ = np.zeros(shape=(10, 10), dtype='int64')
    idx = 0
    for j in range(img_.shape[1]):
        for i in range(img_.shape[0]):
            img_[i, j] = s[idx]
            idx += 1

    return img_


def to_1d(img):
    return np.ravel(img)


def init_spark(app_name):
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

def check_version(python_v, spark_v):
    diff = python_v - spark_v
    is_compatible = True
    for i in range(1, diff.shape[0] - 1):
         for j in range(1, diff.shape[1] - 1):
               for k in range(1, diff.shape[2]):
                   if diff[i, j, k] != 0:
                       is_compatible = False
    if is_compatible is not True:
            print("ERROR : La version spark est incompatible avec la version séquentielle")
    else:
            print("SUCCESS : Les deux versions sont compatibles")

def convert_list_to_3Darray(list, nx, ny, nz):
    tab = np.zeros((nx * ny * nz))
    for index, pixel in list:
        tab[index] = pixel
    cube = np.reshape(tab, (nz, nx, ny))
    return cube

def main():
    np.random.seed(1)
    img = np.random.randint(0, 255, (100, 100, 100))

# Ajout du bruit Gaussien
    t1 = time.process_time()
    img_bruitee = gaussian_noise(img)
    t2 = time.process_time() - t1
    print("TIME OF APPLYING GAUSSIAN NOISE :", t2)

# Appliquer la version séquentielle du filtre médian sur l'image bruitée
    t1 = time.process_time()
    med_fil = median_filter_3D(img)
    t2 = time.process_time() - t1
    print("TIME OF 3D PYTHON VERSION :", t2)
    print(med_fil)

# Partitionner l'image
    t1 = time.process_time()
    images = image_partition3D(img)
    t2 = time.process_time() - t1
    print("TIME OF IMAGE PARTITIONNING :", t2)

# Appliquer la version spark du filtre médian sur l'image
    t1 = time.process_time()
    sc = init_spark("median_filter")
    images_rdd = sc.parallelize(images, 8)
    #print("NB PARTITIONS :", images_rdd.getNumPartitions())
    #print("RDD1 COUNT: ", images_rdd.count())
    neighbors_rdd = images_rdd.flatMap(get_neighbors3D)
    #print("RDD2 COUNT :", neighbors_rdd.count())
    median_rdd = neighbors_rdd.mapValues(sorted_neighbors)
   # print("RDD3 COUNT : ", median_rdd.count())
    res_list = median_rdd.collect()
    t2 = time.process_time() - t1
    print("TIME OF 3D SPARK VERSION", t2)
# Récupérer le résultat dans un tableau 3D
    res_array = convert_list_to_3Darray(res_list, img.shape[0], img.shape[1], img.shape[2])
    #print(res_array)

# Plotter les trois versions
    plt.subplot(1, 3, 1)
    plt.imshow(img[50, :, :])
    plt.subplot(1, 3, 2)
    plt.imshow(med_fil[50, :, :])
    plt.subplot(1, 3, 3)
    plt.imshow(res_array[50, :, :])
    plt.show()

if __name__ == '__main__':
    main()
