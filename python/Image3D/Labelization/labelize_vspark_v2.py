import numpy as np


def compute_idx(i, j, ny):
    idx = j + i * ny
    return idx


def image_partition_bande(img):
    partitions_list = []
    index_array = np.zeros((img.shape[0], img.shape[1]))
    for i in range(index_array.shape[0]):
        for j in range(index_array.shape[1]):
            index_array[i, j] = compute_idx(i, j, index_array.shape[1])

    # Définir la tailles des nouvelles partitions
    if img.shape[0] % 4 != 0:
        print("ERROR : LE NOMBRE DE LIGNES DOIT ETRE UN MULTIPLE de 4:")
    else:
        size_px = img.shape[0] // 4
        size_py = img.shape[1]
    # Définir les nouvelles partitions
    partition1 = np.zeros((2, size_px + 1, size_py + 1), dtype=img.dtype)
    partition2 = np.zeros((2, size_px + 1, size_py + 1), dtype=img.dtype)
    partition3 = np.zeros((2, size_px + 1, size_py + 1), dtype=img.dtype)
    partition4 = np.zeros((2, size_px + 1, size_py + 1), dtype=img.dtype)

    # Remplir les partitions avec les pixels de l'image'
    partition1[0, 1:size_px + 1, 1:size_py + 1] = img[0:size_px, :]
    partition1[1, 1:size_px + 1, 1:size_py + 1] = index_array[0:size_px, :]
    #    partitions_list[0] = partition1
    partitions_list.append((0, partition1))

    partition2[0, 1:size_px + 1, 1:size_py + 1] = img[size_px:2 * size_px, :]
    partition2[0, 0, 1:size_py + 1] = img[size_px - 1, :]
    partition2[1, 1:size_px + 1, 1:size_py + 1] = index_array[size_px:2 * size_px, :]
    partition2[1, 0, 1:size_py + 1] = index_array[size_px - 1, :]
    #   partitions_list[1] = partition2
    partitions_list.append((1, partition2))

    partition3[0, 1:size_px + 1, 1:size_py + 1] = img[2 * size_px:3 * size_px, :]
    partition3[0, 0, 1:size_py + 1] = img[2 * size_px - 1, :]
    partition3[1, 1:size_px + 1, 1:size_py + 1] = index_array[2 * size_px:3 * size_px, :]
    partition3[1, 0, 1:size_py + 1] = index_array[2 * size_px - 1, :]
    #   partitions_list[2] = partition3
    partitions_list.append((2, partition3))

    partition4[0, 1:size_px + 1, 1:size_py + 1] = img[3 * size_px:img.shape[0], :]
    partition4[0, 0, 1:size_py + 1] = img[3 * size_px - 1, :]
    partition4[1, 1:size_px + 1, 1:size_py + 1] = index_array[3 * size_px:img.shape[0]]
    partition4[1, 0, 1:size_py + 1] = index_array[3 * size_px - 1, :]
    #   partitions_list[3] = partition4
    partitions_list.append((3, partition4))

    return partitions_list


def Labelize_v4(tuple_par):
    (index, partition) = tuple_par
    labels = np.zeros((partition.shape[0], partition.shape[1], partition.shape[2]), dtype=int)
    labels[1, :, :] = partition[1, :, :]
    cpt = index * partition.shape[1] * partition.shape[2]
    conflicts = {}
    for i in range(partition.shape[1]):
        previous = 0
        for j in range(partition.shape[2]):
            value = partition[0, i, j]
            if value == 1:
                if j > 0 and previous > 0:
                    labels[0, i, j] = labels[0, i, j - 1]
                    # get potential conflicts
                    if i > 0:
                        up_label = labels[0, i - 1, j]
                        if partition[0, i - 1, j] > 0 and up_label != previous:
                            if up_label not in conflicts:
                                conflicts[up_label] = previous

                elif i > 0 and partition[0, i - 1, j] > 0:
                    labels[0, i, j] = labels[0, i - 1, j]
                else:
                    cpt += 1
                    labels[0, i, j] = cpt
                previous = labels[0, i, j]
            else:
                previous = 0

    for i in range(partition.shape[1]):
        for j in range(partition.shape[2]):
            value = labels[0, i, j]
            if value in conflicts:
                labels[0, i, j] = conflicts[value]

    return (index, labels)


def first_pass(partition):
    label = np.zeros((partition.shape[1], partition.shape[2]), dtype=int)
    res_list = []
    cpt = 0
    for i in range(1, partition.shape[1]):
        for j in range(1, partition.shape[2]):
            if partition[0, i, j] == 1:
                # cas d'un composant connecté
                if partition[0, i, j - 1] == 1:
                    label[i, j] = label[i, j - 1]
                    if partition[0, i - 1, j] == 1:
                        res_list.append((partition[1, i, j], [label[i, j], label[i - 1, j]]))
                    else:
                        res_list.append((partition[1, i, j], [label[i, j]]))

                elif partition[0, i - 1, j] == 1:
                    label[i, j] = label[i - 1, j]
                    res_list.append((partition[1, i, j], [label[i, j]]))

                # cas d'un composant non connecté
                else:
                    cpt += 1
                    label[i, j] = cpt
                    res_list.append((partition[1, i, j], [label[i, j]]))
    return res_list


def second_pass(n_list):
    (index, partition) = n_list
    res_list = []
    res_list.append((index, partition[0, 0, :]))
    res_list.append((index + 1, partition[0, partition.shape[1] - 1, :]))
    return res_list


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
                if array_tuple[0][i] > 0 and array_tuple[1][i] > 0:
                    if array_tuple[0][i] != array_tuple[1][i]:
                        conf_list.append((array_tuple[0][i], array_tuple[1][i]))
    return conf_list


def correct_conflicts_best(n_list):
    res_list = n_list
    for key, label in n_list:
        for key2, label2 in n_list:
            if key == label2:
                if (key, label) in res_list:
                    res_list.remove((key, label))
                    # res_list.append((min(label, key), max(key2, label)))
                    res_list.append((key2, label))
                    res_list.append((min(label, key2), key))
    return res_list


def correct_conflicts(n_list):
    res_list = []
    c_list = []
    for key, label in n_list:
        for key2, label2 in n_list:
            if (key, label) != (key2, label2):
                if label == key2:
                    c_list.append(label2)
                elif label == label2:
                    c_list.append(key2)
        if c_list == []:
            res_list.append((key, label))
        else:
            res_list.append((min(c_list), label))
            for s in c_list:
                 res_list.append((min(c_list), s))
    tmp_list = []
    for key, label in res_list:
        if (key, label) not in tmp_list:
            tmp_list.append((key, label))
    return tmp_list


def correct_labels_v3(n_list, element):
    (index, partition) = n_list
    for i in range(partition.shape[1]):
        for j in range(partition.shape[2]):
            for key, label in element:
                if partition[0, i, j] == label:
                    partition[0, i, j] = key
    return index, partition


if __name__ == '__main__':
    np.random.seed(1)
    tab = np.random.randint(0, 2, (20, 20))
    print(tab)
    partitions_list = image_partition_bande(tab)
    print("Partition  0:", partitions_list[0])
    print("Partition 1:", partitions_list[1])
    print("Partition 2:", partitions_list[2])
    print("Partition 3:", partitions_list[3])
