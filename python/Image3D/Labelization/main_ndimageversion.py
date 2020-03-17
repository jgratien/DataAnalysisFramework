import sys

sys.path.append('..')

import numpy as np
from array_part import array_split_band
from ndimage_labelize import compute_idx3D, labelize, second_pass, detect_conflicts, correct_labels, detect_conflicts_v2
from pyspark import SparkContext, SparkConf
import time
from functools import partial
from Gauss_elimination import *
from CCL3D import CCL3D, Conflicts, resolve_labels_conflits_v2
from scipy.ndimage import label
from conflits_solver import solve, solveV2


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
    size_par = (res_list[0][1].shape[0] - 1) * res_list[0][1].shape[1] * res_list[0][1].shape[2]
    for index, partition in res_list:
        offset = index * size_par
     #   print("OFFSET OF PARTITION :", offset)
        for z in range(1, partition.shape[0] - 1):
            for y in range(partition.shape[1]):
                for x in range(partition.shape[2]):
                         tab[offset + x + y * partition.shape[2] + z * partition.shape[1] * partition.shape[2]] = partition[z, y, x]
    cube = np.reshape(tab, (nx, ny, nz))
    return cube


def main():
    np.random.seed(1)
    img = np.random.randint(0, 2, (200, 200, 200)).astype(np.float32)
    # img = np.random.randint(0, 2, (32, 8, 8)).astype(np.float32)
    #    print(img)

    # Partitionner l'image en 4 bandes
    images = array_split_band(img, 2)
#    print(images)

    t1 = time.process_time()
    res_ndimage = label(img)
    t2 = time.process_time() - t1
    print("TIME OF ND_IMAGE VERSION ON ALL IMAGE:", t2)

    tmp_list = []
    for s in images:
        idx,res = labelize(s)
        tmp_list.append(res)


    total_cpt=0
    conflits_list = []
    for t in tmp_list:
        t3 = time.process_time()
        t2 = second_pass((t[0],t))
        t4 = time.process_time() - t3
        print("\t TIME OF SECOND PASS :", t4)

        t3 = time.process_time()
        conf, cpt = detect_conflicts_v2((t[0],t2))
        t4 = time.process_time() - t3
        print("\t TIME OF DETEC CONFLICTS :", t4)
        print("\t NB CONFLICTS :", cpt)
        conflits_list.append((conf,cpt))
        total_cpt += cpt

    print("TOTAL NB CONFLICTS :",total_cpt)
    conflits = np.zeros((total_cpt,2),dtype=int)    
    conflits2 = np.zeros([2*total_cpt],dtype=np.int32)
    ic=0
    for c,c_size in conflits_list:
        conflits[ic:ic+c_size,:] = np.copy(conf[:c_size,:])
        for i in range(c_size):
            conflits2[2*(ic+i)] = conf[i][0]
            conflits2[2*(ic+i)+1] = conf[i][1]
            print("CONFLITS",ic+i,conf[i][0],conf[i][1])
        ic+=c_size
    t3 = time.process_time()
    res = resolve_labels_conflits_v2(conflits, total_cpt)
    #print(res)
    t4 = time.process_time() - t3
    print("TIME OF CORRECTION OF CONFLICTS SECOND VERSION:", t4)
    
    
    t3 = time.process_time()
    #nb_label,res_list = solveV2(conflits2,total_cpt)
    t4 = time.process_time() - t3
    print("TIME OF CORRECTION OF CONFLICTS CYTHON VERSION 2:", t4)
    #print(res_list)
    
    t3 = time.process_time()
    nb_label,res_list = solve(conflits2,total_cpt)
    #print(res)
    t4 = time.process_time() - t3
    print("TIME OF CORRECTION OF CONFLICTS CYTHON VERSION 1:", t4)
    return
    t3 = time.process_time()
    conflicts = Conflicts()
    idx_max = conflicts.set_connected(conf)
    mapping = conflicts.merge(idx_max)
    # print(mapping)
    t4 = time.process_time() - t3
    print("CORRECTION CONFLICTS FIRST VERSION TIME :", t4)
    return

    # Lancer la version spark
    t1 = time.process_time()
    sc = init_spark(" Labelize_filter")

    l4j = sc._jvm.org.apache.log4j
    LOGGER = l4j.LogManager.getLogger(__name__)

    images_rdd = sc.parallelize(images, 4)

    # Affecter un label pour chaque pixel
    first_rdd = images_rdd.map(labelize)
    #print(" RESUTAT DU PREMIER PASS : \n", first_rdd.collect())

    # Deuxième Pass pour repérer les conflits
    second_rdd = first_rdd.flatMap(second_pass)
    #print(" RESULTAT DU SECOND PASS : \n", second_rdd.collect())


    # Regrouper les lignes ayant les mêmes clés
    last_rdd = second_rdd.groupByKey()
    #print(" RESULTAT FINAL : \n", last_rdd.collect())

    # Repérer les conflits
    conflicts_rdd = last_rdd.flatMap(detect_conflicts)
   # print(conflicts_rdd.collect())

    conflicts_list = conflicts_rdd.collect()
    LOGGER.warn("need to resolve {}".format(len(conflicts_list)))
    t3 = time.process_time()
    conflicts = Conflicts()
    idx_max = conflicts.set_connected(conflicts_list)
    mapping = conflicts.merge(idx_max)
    t4 = time.process_time() - t3
    print("CORRECTION CONFLICTS TIME :", t4)

    # Diffuser le dictionnaire des conflits pour toutes les partition
    cpt_bcast = sc.broadcast(mapping)
   # LOGGER.warn(" Dictionnaire broadcasté : {}".format(cpt_bcast.value))

    mapper = partial(correct_labels, mapping=cpt_bcast.value)

    # Corriger les conflits
    final_rdd = first_rdd.map(mapper)
   # print(" RESULTAT FINAL : \n", final_rdd.collect())


    # Réstituer l'image de labels
    res_final = recover_image(final_rdd.collect(), img.shape[0], img.shape[1], img.shape[2])
    t2 = time.process_time() - t1
    LOGGER.warn(" TIME OF SPARK VERSION : {}".format(t2))
    print("RESULT OF SPARK VERSION : \n", res_final)

    t1 = time.process_time()
    res_ndimage = label(img)
    t2 = time.process_time() - t1
    print("RESULT OF ND_IMAGE VERSION :", res_ndimage)
    print("TIME OF ND_IMAGE VERSION :", t2)



if __name__ == '__main__':
    main()


"""
 for i in range(img.shape[1]):
        for j in range(img.shape[2]):
            for k in range(img.shape[3]):
                img[1, i, j, k] = compute_idx3D(i, j, k, img.shape[2], img.shape[3])
    
"""
