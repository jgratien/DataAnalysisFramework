import numpy as np
from Median_filter.median_vspark2D import image_partition
from Median_filter.median_vspark2D import median_filter_2D
from Median_filter.median_vspark3D import median_filter_3D
from Median_filter.median_vspark3D import image_partition3D
import time


def main():
    np.random.seed(1)
    img_2D = np.random.randint(0, 2, (2000, 2000))
    # Tester la version séquentielle 2D
    # Appliquer la version séquentielle sur toute l'image
    t1 = time.process_time()
    median_fil = median_filter_2D(img_2D)
    t2 = time.process_time() - t1
    print("TIME OF ALL IMAGE WITH 2D PYTHON VERSION :", t2)

    # Appliquer la version séquentielle sur chaque partition de l'image
    images = image_partition(img_2D)
    t1 = time.process_time()
    median_fil = median_filter_2D(images[0][1][0, :])
    t2 = time.process_time() - t1
    print("TIME OF ONE PARTITION WITH 2D PYTHON VERSION  :", t2, "\n")


    print("******************************************* \n")
    # Tester la version séquentielle 3D
    np.random.seed(1)
    img_3D = np.random.randint(0, 2, (100, 100, 100))
    # Appliquer la version séquentielle sur toute l'image
    t1 = time.process_time()
    med_res = median_filter_3D(img_3D)
    t2 = time.process_time() - t1
    print("TIME OF ALL IMAGE WITH 3D PYTHON VERSION :", t2)

    # Appliquer la version séquentielle sur chaque partition de l'image
    images_3D = image_partition3D(img_3D)
    t1 = time.process_time()
    med_res = median_filter_3D(images_3D[0][1][0, :, :, :])
    t2 = time.process_time() - t1
    print("TIME OF ONE PARTITION WITH 3D PYTHON VERSION  :", t2)


if __name__ == '__main__':
        main()



