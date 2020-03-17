import numpy as np


def compute_idx(i, j, ny):
    idx = j + i * ny
    return idx


def get_idx(idx, ny):
    i = idx / ny
    j = idx % ny
    return i, j


def image_partition(img):
    partitions_list = []
    index_array = np.zeros((img.shape[0], img.shape[1]))
    for i in range(index_array.shape[0]):
        for j in range(index_array.shape[1]):
            index_array[i, j] = compute_idx(i, j, index_array.shape[1])

    # Définir la tailles des nouvelles partitions
    size_px = img.shape[0] // 2
    size_py = img.shape[1] // 2
    # Définir les nouvelles partitions
    partition1 = np.zeros((2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition2 = np.zeros((2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition3 = np.zeros((2, size_px + 2, size_py + 2), dtype=img.dtype)
    partition4 = np.zeros((2, size_px + 2, size_py + 2), dtype=img.dtype)

    # Remplir les partitions avec les pixels de l'image'
    partition1[0, 1:size_px + 1, 1:size_py + 1] = img[0:size_px, 0:size_py]
    partition1[0, size_px + 1, :] = img[size_px, 0:size_py + 2]
    partition1[0, :, size_py + 1] = img[0:size_px + 2, size_py]

    # Remplir les partitions avec les indices des pixels
    partition1[1, 1:size_px + 1, 1:size_py + 1] = index_array[0:size_px, 0:size_py]
    partition1[1, size_px + 1, :] = index_array[size_px, 0:size_py + 2]
    partition1[1, :, size_py + 1] = index_array[0:size_px + 2, size_py]
    partitions_list.append(partition1)

    partition2[0, 1:size_px + 1, 1:size_py + 1] = img[0:size_px, size_py:img.shape[1]]
    partition2[0, size_px + 1, :] = img[size_px, 0:size_py + 2]
    partition2[0, :, 0] = img[0:size_px + 2, size_py - 1]

    partition2[1, 1:size_px + 1, 1:size_py + 1] = index_array[0:size_px, size_py:img.shape[1]]
    partition2[1, size_px + 1, :] = index_array[size_px, 0:size_py + 2]
    partition2[1, :, 0] = index_array[0:size_px + 2, size_py - 1]
    partitions_list.append(partition2)

    partition3[0, 1:size_px + 1, 1:size_py + 1] = img[size_px:img.shape[0], 0:size_py]
    partition3[0, 0, :] = img[size_px - 1, 0:size_py + 2]
    partition3[0, :, size_py + 1] = img[0:size_px + 2, size_py]
    partition3[1, 1:size_px + 1, 1:size_py + 1] = index_array[size_px:img.shape[0], 0:size_py]
    partition3[1, 0, :] = index_array[size_px - 1, 0:size_py + 2]
    partition3[1, :, size_py + 1] = index_array[0:size_px + 2, size_py]
    partitions_list.append(partition3)

    partition4[0, 1:size_px + 1, 1:size_py + 1] = img[size_px:img.shape[0], size_py:img.shape[1]]
    partition4[0, 0:size_px + 1, 0] = img[size_px - 1:img.shape[0], size_py - 1]
    partition4[0, 0, 0:size_py + 1] = img[size_px - 1, size_py - 1:img.shape[1]]
    partition4[1, 1:size_px + 1, 1:size_py + 1] = index_array[size_px:img.shape[0], size_py:img.shape[1]]
    partition4[1, 0:size_px + 1, 0] = index_array[size_px - 1:img.shape[0], size_py - 1]
    partition4[1, 0, 0:size_py + 1] = index_array[size_px - 1, size_py - 1:img.shape[1]]
    partitions_list.append(partition4)

    return partitions_list


def median_filter_2D(img):
    M = np.copy(img)
    n_pixel = np.zeros((9))
    for i in range(M.shape[0]-1):
      for j in range(M.shape[1]-1):
         if j > 0 and i > 0:
            n_pixel[0] = img[i-1, j-1]
            n_pixel[1] = img[i-1, j]
            n_pixel[2] = img[i-1, j+1]
            n_pixel[3] = img[i, j-1]
            n_pixel[4] = img[i, j]
            n_pixel[5] = img[i, j+1]
            n_pixel[6] = img[i+1, j-1]
            n_pixel[7] = img[i+1, j]
            n_pixel[8] = img[i+1, j+1]
            s = np.sort(n_pixel, axis=None)
            M[i,j] = s[4]
    # Gérer les bordures
    M[0, :] = np.median(np.sort(M[0, :]))  # (np.sort(M[0, 0, :]))
    M[:, 0] = np.median(np.sort(M[:, 0]))  # (np.sort(M[0, 0, 0]))
    M[M.shape[0] - 1, :] = np.median(np.sort(M[M.shape[0] - 1, :]))
    M[:, M.shape[1] - 1] = np.median(np.sort(M[:, M.shape[1] - 1]))
    return M


def get_neighbors(partition):
    res_list = []
    for i in range(1, partition.shape[1] - 1):
        for j in range(1, partition.shape[2] - 1):
            v_list = [
                partition[0, i, j],
                partition[0, i, j + 1], partition[0, i, j - 1],
                partition[0, i - 1, j], partition[0, i + 1, j],
                partition[0, i - 1, j - 1], partition[0, i - 1, j + 1],
                partition[0, i + 1, j - 1], partition[0, i + 1, j + 1]
            ]
            res_list.append((partition[1, i, j], v_list))

    return res_list


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
    # Lecture de l'image
    # image = imageio.imread("/home/irsrvhome1/R11/amaroucl/local/images_test/image_bruitee.gif")
    # im = np.array(image)
    np.random.seed(1)
    tab = np.random.randint(0, 255, (10, 10))
    partitions_list = image_partition(tab)
    print("Partition 0:", partitions_list[0])
    print("Partition 1:", partitions_list[1])
    print("Partition 2:", partitions_list[2])
    print("Partition 3:", partitions_list[3])
    v = get_neighbors(partitions_list[3])
    print("neighbors list :", v)
