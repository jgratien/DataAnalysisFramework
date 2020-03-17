import numpy as np
from Labelize_algorithm.labelize_vspark3D_v2 import image_partition3D_bande_v2, Labelize_v4, second_pass, detect_conflicts, correct_labels, compute_idx3D
from pyspark import SparkContext, SparkConf
import time
from functools import partial
from Labelize_algorithm.Gauss_elimination import *

def init_spark(app_name):
    sc_conf = SparkConf()
    sc_conf.setAppName(app_name)
    sc_conf.setMaster('local[*]')
    sc_conf.set('spark.executor.memory', '4g')
    sc_conf.set('spark.executor.cores', '4')
    sc_conf.set('spark.driver.memory', '16G')
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


def recover_image(res_list, nx, ny, nz):
    tab = np.zeros((nx * ny * nz), dtype=int)
    for index, partition in res_list:
        for i in range(1, partition.shape[1]):
            for j in range(1, partition.shape[2]):
                for k in range(1, partition.shape[3]):
                    tab[partition[1, i, j, k]] = partition[0, i, j, k]
    cube = np.reshape(tab, (nx, ny, nz))
    return cube





def main():
    np.random.seed(1)
    img = np.random.randint(0, 2, (4, 4, 4))
    print(img)
    # Partitionner l'image en 4 bandes
#    images = image_partition3D_bande_v2(img, 1)
    labels = np.zeros((2, img.shape[0], img.shape[1], img.shape[2]), dtype=img.dtype)
    labels[0, :, :, :] = np.copy(img)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            for k in range(img.shape[2]):
                labels[1, i, j, k] = compute_idx3D(i, j, k, img.shape[1], img.shape[2])

    #    print(images)
    images = [(0, labels)]
    (index, labels) = Labelize_v4(images[0])
    print("RESULTAT :", (index,  labels))
    exit(0)
    # Lancer la version spark
    t1 = time.process_time()
    sc = init_spark(" Labelize_filter")
    images_rdd = sc.parallelize(images, 1)

    # Affecter un label pour chaque pixel
    first_rdd = images_rdd.map(Labelize_v4)
#    print(" RESUTAT DU PREMIER PASS : \n", first_rdd.collect())

    # Deuxiéme Pass pour repérer les conflits
    second_rdd = first_rdd.flatMap(second_pass)
#    print(" RESULTAT DU SECOND PASS : \n", second_rdd.collect())

    # Regrouper les lignes ayant les mêmes clés
    last_rdd = second_rdd.groupByKey()
#    print(" RESULTAT FINAL : \n", last_rdd.collect())

    # Repérer les conflits
    conflicts_rdd = last_rdd.flatMap(detect_conflicts)

    # Diffuser le dictionnaire des conflits pour toutes les partition
    cpt_bcast = sc.broadcast(sc.parallelize(conflicts_rdd.collect()).collectAsMap())
#    print(" Dictionnaire broadcasté : \n", cpt_bcast.value)

    mapper = partial(correct_labels, element=cpt_bcast.value)

    # Corriger les conflits
    final_rdd = first_rdd.map(mapper)
#    print(" RESULTAT FINAL : \n", final_rdd.collect())

    t2 = time.process_time() - t1
    print(" TIME OF SPARK VERSION :", t2)

    # Réstituer l'image de labels
    res_final = recover_image(final_rdd.collect(), img.shape[0], img.shape[1], img.shape[2])
    print(res_final)


if __name__ == '__main__':
    main()


"""
 conf_list = conflicts_rdd.distinct().collect()

    time_list = []
    for i in range(100):
        t0 = time.process_time()
        mat, nc, nl = convert_list_to_matrix(conf_list)
        conflicts_reduction(mat)
        #    print("RESULTAT : \n", mat)
        X = system_resolution(mat)
        t1 = time.process_time() - t0
        time_list.append(t1)
    print("TIME OF FIRST VERSION :", mean(time_list))
    print(X)
    time_list2 = []
    for i in range(100):
        t0 = time.process_time()
        X = resolve_labels_conflits(conf_list)
        t1 = time.process_time() - t0
        time_list2.append(t1)
    print("TIME VERSION OPTIMISEE :", mean(time_list2))
    print(X)
    
"""