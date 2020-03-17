import numpy as np
class Image3D:

    def __init__(self, array):
        self.id = None
        self.name = None
        self.cube = array
        self.header = None

    # Transformer le tableau en 3D en un tableau 1D
    def convert_3D_to_1D(img):
        size_z = img.shape[0]
        size_x = img.shape[1]
        size_y = img.shape[2]
        tab = np.zeros(size_x * size_y * size_z)
        for i in range(size_z):
            for j in range(size_x):
                for k in range(size_y):
                    tab[k + j * size_y + i * size_x * size_y] = img.cube[i, j, k]
        return tab

    # Convertir l'image en gris en utilisant une combinaison linéaire
    def convert_to_gris(image):
        R = image[:, :, :, 0]  # on prend tous les pixels rouges
        G = image[:, :, :, 1]  # on prend tous les pixels verts
        B = image[:, :, :, 2]  # on prend tous les pixels bleus
        im_gris = (.299 * R) + (.587 * G) + (
                    .114 * B)  # On fait une combinaison linéaire entre tous les pixels pour avoir une image en gris
        return im_gris

    # Convertir l'mage en gris en utilisant la  moyenne des pixels
    def convert_to_gris_v2(image):
        im = image[..., :3]
        im_gris = np.mean(im, axis=2)
        return im_gris

    # Filtre médian pour corriger une image bruitée
    def median_filter_3D(img):
        M = np.copy(img)
        # Créer un filtre 3x3
        n_pixel = np.zeros((9))
        for i in range(M.shape[0]):
            for j in range(M.shape[1] - 1):
                for k in range(M.shape[2] - 1):
                    if j > 0 and k > 0:
                        n_pixel[0] = M[i, j - 1, k - 1]
                        n_pixel[1] = M[i, j - 1, k]
                        n_pixel[2] = M[i, j - 1, k + 1]
                        n_pixel[3] = M[i, j, k - 1]
                        n_pixel[4] = M[i, j, k]
                        n_pixel[5] = M[i, j, k + 1]
                        n_pixel[6] = M[i, j + 1, k - 1]
                        n_pixel[7] = M[i, j + 1, k]
                        n_pixel[8] = M[i, j + 1, k + 1]
                        s = np.sort(n_pixel, axis=None)
                        M[i, j, k] = s[4]

        # Gérer les bordures
        for k in range(M.shape[0]):
            M[k, 0, :] = np.median(np.sort(M[k, 0, :]))  # (np.sort(M[0, 0, :]))
            M[k, :, 0] = np.median(np.sort(M[k, :, 0]))  # (np.sort(M[0, 0, 0]))
            M[k, M.shape[1] - 1, :] = np.median(np.sort(M[k, M.shape[1] - 1, :]))
            M[k, :, M.shape[2] - 1] = np.median(np.sort(M[k, :, M.shape[2] - 1]))
        return M

    def noisy(image):
        row, col, p = image.shape
        mean = 0
        var = 10
        sigma = var ** 0.5
        gauss = np.random.normal(mean, sigma, (row, col, p))
        gauss = gauss.reshape(row, col, p)
        noisy = gauss
        return noisy

    def get_nx(self):
        return self.cube.shape[1]

    def get_ny(self):
        return self.cube.shape[2]

    def get_nz(self):
        return self.cube.shape[0]

    def set_value(self, i, j, k, value):
        self.cube[k, i, j] = value

    def get_value(self, i, j, k):
        return self.cube[k, i, j]
