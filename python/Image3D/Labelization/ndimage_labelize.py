import numpy as np
from scipy.ndimage import label
import time

def labelize(p_dict):
    idx = p_dict['idx']
    array = p_dict['array']
    # offset = idx * array.shape[2] * array.shape[3]
    t0 = time.process_time()
    labels = label(array[0, :, :, :])
    t1 = time.process_time() - t0
    print("TIME OF ND_IMAGE VERSION ON ONE PARTITION :", t1)
    return idx, labels[0]



"""
    for i in range(array.shape[1]):
        for j in range(array.shape[2]):
            for k in range(array.shape[3]):
                    labels[0][i, j, k] += offset
"""


def compute_idx3D(i, j, k, nx, ny):
    idx = k + j * ny + i * nx * ny
    return idx

def second_pass(n_list):
    (index, partition) = n_list
    res_list = []
    res_list.append((index, partition[:, 0, :]))
    res_list.append((index + 1, partition[:, partition.shape[1] - 1, :]))
    return res_list

def label_index(Li, Lj):
    if Li < Lj:
        return ((Li * (Li + 1)) // 2) + Lj
    else:
        return ((Lj * (Lj + 1)) // 2) + Li


def detect_conflicts_v2(n_list):
    (index, arrays) = n_list
    tmp_list = []
    for array1 in arrays:
        tmp_list.append(array1)

    if len(tmp_list) == 2:
        array_tuple = (tmp_list[0][1], tmp_list[1][1])
        if array_tuple[0] is not None:
            conf_list = np.zeros((array_tuple[0].shape[0] * array_tuple[0].shape[1], 2), dtype=int)
            conf_set = set()
            cpt = 0
            t0 = time.process_time()
            for i in range(array_tuple[0].shape[0]):
                for j in range(array_tuple[0].shape[1]):
                    if array_tuple[0][i, j] > 0 and array_tuple[1][i, j] > 0:
                        if array_tuple[0][i][j] != array_tuple[1][i][j]:
                            Li = int(array_tuple[0][i, j])
                            Lj = int(array_tuple[1][i, j])
                            Lij_index = label_index(Li, Lj)
                            if Lij_index not in conf_set:
                                conf_list[cpt][0] = Li
                                conf_list[cpt][1] = Lj
                                conf_set.add(Lij_index)
                                cpt += 1
            t1 = time.process_time() - t0
            print("TIME OF LOOP :", t1)
            return conf_list, cpt

    return None


def detect_conflicts(n_list):
    (index, arrays) = n_list
    conf_list = []
    tmp_list = []
    for array1 in arrays:
        tmp_list.append(array1)
    if len(tmp_list) == 2:
        array_tuple = (tmp_list[0], tmp_list[1])
        if array_tuple[0] is not None:
            for i in range(array_tuple[0].shape[0]):
                for j in range(array_tuple[0].shape[1]):
                    if array_tuple[0][i, j] > 0 and array_tuple[1][i, j] > 0:
                        if array_tuple[0][i][j] != array_tuple[1][i][j]:
                            conf_list.append((array_tuple[0][i, j], array_tuple[1][i, j]))
    return conf_list


def correct_conflicts(n_list):
    res_list = n_list
    for key, label in n_list:
        for key2, label2 in n_list:
            if key == label2:
                if (key, label) in res_list:
                    res_list.remove((key, label))
                    res_list.append((key2, label))
                    res_list.append((min(label, key2), key))
    return res_list


def correct_labels(n_list, mapping):
    (index, partition) = n_list
    for i in range(partition.shape[0]):
        for j in range(partition.shape[1]):
            for k in range(partition.shape[2]):
              #  for key, label in mapping.items():
                    value = partition[i, j, k]
                    if value in mapping:
                        partition[i, j, k] = mapping[value]
    return index, partition


if __name__ == '__main__':
    np.random.seed(1)
    img = np.random.randint(0, 2, (8, 32, 8))
    print(img)
    partitions_list = image_partition3D_bande_v2(img, 32)
    print(partitions_list)
