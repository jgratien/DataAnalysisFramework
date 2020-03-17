

def init_spark(app_name):
    from pyspark import SparkContext, SparkConf
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



def main():
    import sys
    import time
    import numpy as np
    from array_part import array_split_band
    from ndimage_labelize import compute_idx3D, labelize, second_pass, detect_conflicts, correct_labels, detect_conflicts_v2
    from CCL3D import CCL3D, Conflicts, resolve_labels_conflits_v2
    from scipy.ndimage import label

    np.random.seed(1)
    img = np.random.randint(0, 2, (100, 100, 100)).astype(np.float32)
    # img = np.random.randint(0, 2, (32, 8, 8)).astype(np.float32)
    #    print(img)
    
    ####################################
    #
    # FIRST TRY TO PROCESS THE ALL IMAGE (IMPOSSIBLE IF IMAGE CANNOT FIT IN MEMORY)
    #
    t1 = time.process_time()
    res_ndimage = label(img)
    t2 = time.process_time() - t1
    print("TIME OF ND_IMAGE VERSION ON ALL IMAGE:", t2)


    # Partitionner l'image en 4 bandes
    nb_partition = 4
    images = array_split_band(img, nb_partition)
#    print(images)
    
    ##################################################
    #
    # LOOP ON PARTITION TO EMULATE PARALLELISME
    #
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
    ic=0
    for c,c_size in conflits_list:
        conflits[ic:ic+c_size,:] = np.copy(conf[:c_size,:])
        ic+=c_size
    t3 = time.process_time()
    
    res = resolve_labels_conflits_v2(conflits, total_cpt)
    #print(res)
    t4 = time.process_time() - t3
    print("TIME OF CORRECTION OF CONFLICTS SECOND VERSION:", t4)



    ##################################################
    #
    # SPARK VERSION
    #
    
    
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
