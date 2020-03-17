import numpy as np
import matplotlib.pyplot as plt
import findspark
findspark.init()
import pyspark
from median_vspark2D import image_partition, get_neighbors, median_filter_2D, sorted_neighbors
from pyspark import SparkContext, SparkConf
import time
import imageio

def create_dummy():
    s = np.random.normal(128, 5, 100)
    img_ = np.zeros(shape=(10, 10), dtype=np.uint8)
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


def read_image(path):
    img = imageio.imread(path)
    im = np.array(img, dtype='int64')
    return im


def main():
   # img = read_image('images_test2D/image_bruitee.gif')
    np.random.seed(1)
    img = np.random.randint(0, 255, (1000, 1000))
    t1 = time.process_time()
    med_fil = median_filter_2D(img)
    t2 = time.process_time() - t1
    print("TIME OF 2D PYTHON VERSION :", t2)
    print(med_fil)

    images = image_partition(img)
    t1 = time.process_time()
    sc = init_spark("Median_filter")
    images_rdd = sc.parallelize(images, 4)
    # print("NB PARTITIONS :", images_rdd.getNumPartitions())
    neighbors_rdd = images_rdd.flatMap(get_neighbors)
    median_rdd = neighbors_rdd.mapValues(sorted_neighbors)
    # print(neighbors_rdd.collect())
    # print(median_rdd.collect())
    res = median_rdd.collect()
    t2 = time.process_time() - t1
    print("TIME OF 2D SPARK VERSION", t2)
    tab = np.zeros((img.shape[0] * img.shape[1]), dtype='int64')
    for index, pixel in res:
        tab[index] = pixel
    cube = np.reshape(tab, (img.shape[0], img.shape[1]))
    print(cube)
    print(cube.shape)

# Plotter les trois versions
    plt.subplot(1, 3, 1)
    plt.imshow(img)
    plt.subplot(1, 3, 2)
    plt.imshow(med_fil)
    plt.subplot(1, 3, 3)
    plt.imshow(cube)
    plt.show()

    # Vérifier que les deux versions sont compatibles
    diff = med_fil - cube
    print(diff)



if __name__ == '__main__':
    main()
