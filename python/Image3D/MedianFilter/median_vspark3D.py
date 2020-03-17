import numpy as np


def compute_idx3D(i, j, k, nx, ny):
    idx = k + j * ny + i * nx * ny
    return idx


def image_partition3D_bande_v2(img, n):
    partitions_list = []
    index_array = np.zeros((img.shape[0], img.shape[1], img.shape[2]), dtype=img.dtype)
    for i in range(index_array.shape[0]):
        for j in range(index_array.shape[1]):
            for k in range(index_array.shape[2]):
                index_array[i, j, k] = compute_idx3D(i, j, k, index_array.shape[1], index_array.shape[2])

    # Définir la tailles des nouvelles partitions
    if img.shape[1] % n != 0:
        print("/!\ ERROR /!\ : LE NOMBRE DE LIGNES DOIT ETRE UN MULTIPLE de 4")
    else:
        size_px = img.shape[1] // n
        size_py = img.shape[2]
        size_pz = img.shape[0]

    # Définir les nouvelles partitions
    par_list = {}
    for i in range(n):
        par_list[i] = np.zeros((2, size_pz, size_px + 2, size_py + 2), dtype=img.dtype)

    for i in range(n):
        # Remplir les partitions avec les pixels de l'image'
        if i == 0:
            par_list[i][0, :, 1:size_px + 1, 1:size_py + 1] = img[:, 0:size_px, :]
            par_list[i][1, :, 1:size_px + 1, 1:size_py + 1] = index_array[:, 0:size_px, :]
            partitions_list.append((0, par_list[i]))
        if i == n - 1:
            par_list[i][0, :, 1:size_px+2, 1:size_py+1] = img[:, i * size_px - 1:img.shape[1], :]
            par_list[i][0, :, 0, 1:size_py + 1] = img[:, i * size_px - 1, :]
            par_list[i][0, :, 1:size_px+2, 1:size_py+1] = index_array[:, i * size_px - 1:img.shape[1], :]
            par_list[i][1, :, 0, 1:size_py + 1] = index_array[:, i * size_px - 1, :]
            partitions_list.append((i, par_list[i]))

        else:
            par_list[i][0, :, 1:size_px + 1, 1:size_py + 1] = img[:, i * size_px:(i + 1) * size_px, :]
            par_list[i][0, :, 0, 1:size_py + 1] = img[:, i * size_px - 1, :]
            par_list[i][1, :, 1:size_px + 1, 1:size_py + 1] = index_array[:, i * size_px:(i + 1) * size_px, :]
            par_list[i][1, :, 0, 1:size_py + 1] = index_array[:, i * size_px - 1, :]
            partitions_list.append((i, par_list[i]))
    return partitions_list


def image_partition3D(img):
    partitions_list = []
    index_array = np.zeros((img.shape[0], img.shape[1], img.shape[2]))
    for i in range(index_array.shape[0]):
        for j in range(index_array.shape[1]):
            for k in range(index_array.shape[2]):
                index_array[i, j, k] = compute_idx3D(i, j, k, index_array.shape[1], index_array.shape[2])
    # Définir la tailles des nouvelles partitions
    size_px = img.shape[0] // 2
    size_py = img.shape[1] // 2
    size_pz = img.shape[2] // 2

    # Définir les nouvelles partitions
    partition1 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition2 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition3 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition4 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition5 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition6 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition7 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition8 = np.zeros((2, size_pz + 2, size_px + 2, size_py + 2), dtype=img.dtype)

    # Remplir la partition 1 avec les pixels de l'image'
    partition1[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[0:size_pz, 0:size_px, 0:size_py]
    partition1[0, 1:size_pz + 1, size_px + 1, :] = img[0:size_pz, size_px, 0:size_py + 2]
    partition1[0, 1:size_pz + 1, :, size_py + 1] = img[0:size_pz, 0:size_px + 2, size_py]
    partition1[0, size_pz + 1, :, :] = img[size_pz, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 1 avec les indices des pixels
    partition1[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[0:size_pz, 0:size_px, 0:size_py]
    partition1[1, 1:size_pz + 1, size_px + 1, :] = index_array[0:size_pz, size_px, 0:size_py + 2]
    partition1[1, 1:size_pz + 1, size_py + 1] = index_array[0:size_pz, 0:size_px + 2, size_py]
    partition1[1, size_pz + 1, :, :] = index_array[size_pz, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition1)

    # Remplir la partition 2 avec les pixels de l'image
    partition2[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[0:size_pz, 0:size_px, size_py:img.shape[2]]
    partition2[0, 1:size_pz + 1, size_px + 1, :] = img[0:size_pz, size_px, 0:size_py + 2]
    partition2[0, 1:size_pz + 1, :, 0] = img[0:size_pz, 0:size_px + 2, size_py - 1]
    partition2[0, size_pz + 1, :, :] = img[size_pz, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 2 avec les pixels de l'image
    partition2[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[0:size_pz, 0:size_px, size_py:img.shape[2]]
    partition2[1, 1:size_pz + 1, size_px + 1, :] = index_array[0:size_pz, size_px, 0:size_py + 2]
    partition2[1, 1:size_pz + 1, :, 0] = index_array[0:size_pz, 0:size_px + 2, size_py - 1]
    partition2[1, size_pz + 1, :, :] = index_array[size_pz, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition2)

    # Remplir la partition 3 avec les pixels de l'image
    partition3[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[0:size_pz, size_px:img.shape[1], 0:size_py]
    partition3[0, 1:size_pz + 1, 0, :] = img[0:size_pz, size_px - 1, 0:size_py + 2]
    partition3[0, 1:size_pz + 1, :, size_py + 1] = img[0:size_pz, 0:size_px + 2, size_py]
    partition3[0, 0, :, :] = img[0, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 3 avec les indices des pixels
    partition3[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[0:size_pz, size_px:img.shape[1], 0:size_py]
    partition3[1, 1:size_pz + 1, 0, :] = index_array[0:size_pz, size_px - 1, 0:size_py + 2]
    partition3[1, 1:size_pz + 1, :, size_py + 1] = index_array[0:size_pz, 0:size_px + 2, size_py]
    partition3[1, 0, :, :] = index_array[0, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition3)

    # Remplir la partition 4 avec les pixels de l'image
    partition4[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[0:size_pz, size_px:img.shape[1],
                                                                 size_py:img.shape[2]]
    partition4[0, 1:size_pz + 1, 0:size_px + 1, 0] = img[0:size_pz, size_px - 1:img.shape[0], size_py - 1]
    partition4[0, 1:size_pz + 1, 0, 0:size_py + 1] = img[0:size_pz, size_px - 1, size_py - 1:img.shape[1]]
    partition4[0, 0, :, :] = img[0, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 4 avec les indices des pixels
    partition4[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[0:size_pz, size_px:img.shape[1],
                                                                 size_py:img.shape[2]]
    partition4[1, 1:size_pz + 1, 0:size_px + 1, 0] = index_array[0:size_pz, size_px - 1:img.shape[0], size_py - 1]
    partition4[1, 1:size_pz + 1, 0, 0:size_py + 1] = index_array[0:size_pz, size_px - 1, size_py - 1:img.shape[1]]
    partition4[1, 0, :, :] = index_array[0, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition4)

    # Remplir la partition 5 avec les pixels de l'image
    partition5[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[size_pz:img.shape[0], 0:size_px, 0:size_py]
    partition5[0, 1:size_pz + 1, size_px + 1, :] = img[size_pz:img.shape[0], size_px, 0:size_py + 2]
    partition5[0, 1:size_pz + 1, :, size_py + 1] = img[size_pz:img.shape[0], 0:size_px + 2, size_py]
    partition5[0, size_pz + 1, :, :] = img[size_pz, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 5 avec les indices des pixels
    partition5[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[size_pz:img.shape[0], 0:size_px, 0:size_py]
    partition5[1, 1:size_pz + 1, size_px + 1, :] = index_array[size_pz:img.shape[0], size_px, 0:size_py + 2]
    partition5[1, 1:size_pz + 1, :, size_py + 1] = index_array[0:size_pz, 0:size_px + 2, size_py]
    partition5[1, size_pz + 1, :, :] = index_array[size_pz, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition5)

    # Remplir la partition 6 avec les pixels de l'image
    partition6[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[size_pz:img.shape[0], 0:size_px,
                                                                 size_py:img.shape[2]]
    partition6[0, 1:size_pz + 1, size_px + 1, :] = img[size_pz:img.shape[0], size_px, 0:size_py + 2]
    partition6[0, 1:size_pz + 1, :, 0] = img[size_pz:img.shape[0], 0:size_px + 2, size_py - 1]
    partition6[0, size_pz + 1, :, :] = img[size_pz, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 6 avec les indices des pixels
    partition6[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[size_pz:img.shape[0], 0:size_px,
                                                                 size_py:img.shape[2]]
    partition6[1, 1:size_pz + 1, size_px + 1, :] = index_array[size_pz:img.shape[0], size_px, 0:size_py + 2]
    partition6[1, 1:size_pz + 1, :, 0] = index_array[size_pz:img.shape[0], 0:size_px + 2, size_py - 1]
    partition6[1, size_pz + 1, :, :] = index_array[size_pz, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition6)

    # Remplir la partition 7 avec les pixels de l'image
    partition7[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[size_pz:img.shape[0], size_px:img.shape[1],
                                                                 0:size_py]
    partition7[0, 1:size_pz + 1, 0, :] = img[size_pz:img.shape[0], size_px - 1, 0:size_py + 2]
    partition7[0, 1:size_pz + 1, :, size_py + 1] = img[size_pz:img.shape[0], 0:size_px + 2, size_py]
    partition7[0, 0, :, :] = img[0, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 7 avec les indices des pixels
    partition7[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[size_pz:img.shape[0], size_px:img.shape[1],
                                                                 0:size_py]
    partition7[1, 1:size_pz + 1, 0, :] = index_array[size_pz:img.shape[0], size_px - 1, 0:size_py + 2]
    partition7[1, 1:size_pz + 1, :, size_py + 1] = index_array[size_pz:img.shape[0], 0:size_px + 2, size_py]
    partition7[1, 0, :, :] = index_array[0, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition7)

    # Remplir la partition 8  avec les pixels de l'image
    partition8[0, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = img[size_pz:img.shape[0], size_px:img.shape[1],
                                                                 size_py:img.shape[2]]
    partition8[0, 1:size_pz + 1, 0:size_px + 1, 0] = img[size_pz:img.shape[0], size_px - 1:img.shape[0], size_py - 1]
    partition8[0, 1:size_pz + 1, 0, 0:size_py + 1] = img[size_pz:img.shape[0], size_px - 1, size_py - 1:img.shape[1]]
    partition8[0, 0, :, :] = img[0, 0:size_px + 2, 0:size_py + 2]
    # Remplir la partition 8 avec les indices des pixels
    partition8[1, 1:size_pz + 1, 1:size_px + 1, 1:size_py + 1] = index_array[size_pz:img.shape[0], size_px:img.shape[1],
                                                                 size_py:img.shape[2]]
    partition8[1, 1:size_pz + 1, 0:size_px + 1, 0] = index_array[size_pz:img.shape[0], size_px - 1:img.shape[0],
                                                     size_py - 1]
    partition8[1, 1:size_pz + 1, 0, 0:size_py + 1] = index_array[size_pz:img.shape[0], size_px - 1,
                                                     size_py - 1:img.shape[1]]
    partition8[1, 0, :, :] = index_array[0, 0:size_px + 2, 0:size_py + 2]
    partitions_list.append(partition8)
    return partitions_list


def get_neighbors3D(partition):
    res_list = []
    for i in range(1, partition.shape[1] - 1):
        for j in range(1, partition.shape[2] - 1):
            for k in range(1, partition.shape[3] - 1):
                v_list = []
                v_list.extend([partition[0, i, j, k], partition[0, i, j + 1, k], partition[0, i, j - 1, k],
                               partition[0, i, j, k - 1], partition[0, i, j + 1, k - 1], partition[0, i, j - 1, k - 1],
                               partition[0, i, j, k + 1], partition[0, i, j + 1, k + 1], partition[0, i, j - 1, k + 1],
                               partition[0, i - 1, j, k], partition[0, i - 1, j - 1, k], partition[0, i - 1, j + 1, k],
                               partition[0, i - 1, j, k - 1], partition[0, i - 1, j - 1, k - 1],
                               partition[0, i - 1, j + 1, k - 1],
                               partition[0, i - 1, j, k + 1], partition[0, i - 1, j - 1, k + 1],
                               partition[0, i - 1, j + 1, k + 1],
                               partition[0, i + 1, j - 1, k], partition[0, i + 1, j, k], partition[0, i + 1, j + 1, k],
                               partition[0, i + 1, j - 1, k - 1], partition[0, i + 1, j, k - 1],
                               partition[0, i + 1, j + 1, k - 1],
                               partition[0, i + 1, j - 1, k + 1], partition[0, i + 1, j, k + 1],
                               partition[0, i + 1, j + 1, k + 1]])
                res_list.append((partition[1, i, j, k], v_list))

    return res_list


def median_filter_3D(img):
    M = np.copy(img)
    # Créer un filtre 3x3
    n_pixel = np.zeros((27))
    for i in range(1, M.shape[0] - 1):
        for j in range(1, M.shape[1] - 1):
            for k in range(1, M.shape[2] - 1):
                n_pixel[0] = img[i, j - 1, k - 1]
                n_pixel[1] = img[i - 1, j - 1, k - 1]
                n_pixel[2] = img[i + 1, j - 1, k - 1]
                n_pixel[3] = img[i, j - 1, k]
                n_pixel[4] = img[i - 1, j - 1, k]
                n_pixel[5] = img[i + 1, j - 1, k]
                n_pixel[6] = img[i, j - 1, k + 1]
                n_pixel[7] = img[i - 1, j - 1, k + 1]
                n_pixel[8] = img[i + 1, j - 1, k + 1]
                n_pixel[9] = img[i, j, k - 1]
                n_pixel[10] = img[i - 1, j, k - 1]
                n_pixel[11] = img[i + 1, j, k - 1]
                n_pixel[12] = img[i, j, k]
                n_pixel[13] = img[i - 1, j, k]
                n_pixel[14] = img[i + 1, j, k]
                n_pixel[15] = img[i, j, k + 1]
                n_pixel[16] = img[i - 1, j, k + 1]
                n_pixel[17] = img[i + 1, j, k + 1]
                n_pixel[18] = img[i, j + 1, k - 1]
                n_pixel[19] = img[i - 1, j + 1, k - 1]
                n_pixel[20] = img[i + 1, j + 1, k - 1]
                n_pixel[21] = img[i, j + 1, k]
                n_pixel[22] = img[i - 1, j + 1, k]
                n_pixel[23] = img[i + 1, j + 1, k]
                n_pixel[24] = img[i, j + 1, k + 1]
                n_pixel[25] = img[i - 1, j + 1, k + 1]
                n_pixel[26] = img[i + 1, j + 1, k + 1]
                s = np.sort(n_pixel, axis=None)
                M[i, j, k] = s[13]
    return M


def gaussian_noise(image):
    row, col, p = image.shape
    mean = 0
    var = 10
    sigma = var ** 0.5
    gauss = np.random.normal(mean, sigma, (row, col, p))
    gauss = gauss.reshape(row, col, p)
    noisy = gauss
    return noisy


def median(l):
    l_len = len(l)
    if l_len < 1:
        return None
    if l_len % 2 == 0:
        return (l[(l_len - 1) // 2] + l[(l_len + 1) // 2]) // 2
    else:
        return l[(l_len - 1) // 2]


def sorted_neighbors(n_list):
    v_list = sorted(n_list)
    v_median = median(v_list)
    return v_median


if __name__ == '__main__':
    np.random.seed(1)
    tab = np.random.randint(0, 2, (8, 8, 8))
    print(tab)
    p_list = image_partition3D_bande_v2(tab, 2)
#    res = get_neighbors3D(p_list[1])
    print(p_list)
