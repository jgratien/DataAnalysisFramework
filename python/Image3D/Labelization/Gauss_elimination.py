import numpy as np
import time


def convert_list_to_matrix(conf_list):
    labels = []
    labels_index = {}
    for label1, label2 in conf_list:
        if label1 not in labels:
            labels_index[label1] = len(labels)
            labels.append(label1)
        if label2 not in labels:
            labels_index[label2] = len(labels)
            labels.append(label2)
    Nl = len(labels)
    Nc = len(conf_list)
    matrix_res = np.zeros((Nc + 1, Nl), dtype=int)
    for k in range(Nl):
        matrix_res[0,labels_index[labels[k]]] = labels[k]
    for k in range(Nc):
        c=conf_list[k]
        j0=labels_index[c[0]]
        j1=labels_index[c[1]]
        matrix_res[k+1, j0] = 1
        matrix_res[k+1, j1] = -1

    return matrix_res, Nc, Nl


def conflicts_reduction(A):
    nc = A.shape[0]-1
    nl = A.shape[1]
    if A.shape[0]-1 <= A.shape[1]:
        for j in range(0, nc):
            max_el = A[j + 1, j]
            idx_col = j
            if max_el == 0:
                is_found = False
                for k in range(j+1, A.shape[1]):
                     # Changer les colonnes
                     if A[j+1, k] != 0:
                         if j != k:
                            idx_col = k
                            is_found = True
                     if is_found is True :
                         break
                if is_found is True:
                    tmp = np.copy(A[:, j])
                    A[:, j] = np.copy(A[:, idx_col])
                    A[:, idx_col] = np.copy(tmp)
            Ajj = A[j + 1, j]

            # Eliminer tous les éléments non nuls de la colonne
            for i in range(j+2, A.shape[0]):
                if A[i, j] != 0:
                    A[i, :] -= A[i, j] // Ajj * A[j+1, :]


def system_resolution(A):
    nl = A.shape[1]
    nc = A.shape[0]-1
    X = np.zeros(nl, dtype=int)
    X[0:nc] = -1
    X[nc:nl] = A[0, nc:nl]
    for i in range(nc-1, -1, -1):
        s = 0
        for j in range(i+1, nl):
            s = s - A[i+1, j] * X[j]
        X[i] = s // A[i+1, i]
    return X


def resolve_labels_conflits(ref_conflits):
    import copy
    conflits=copy.deepcopy(ref_conflits)
    labels = []
    label_conflits = {}
    c_index = 0
    for c in conflits:
        if c[0] not in labels:
            labels.append(c[0])
            label_conflits[c[0]] = [c_index]
        else:
            label_conflits[c[0]].append(c_index)

        if c[1] not in labels:
            labels.append(c[1])
            label_conflits[c[1]] = [c_index]
        else:
            label_conflits[c[1]].append(c_index)
        c_index = c_index + 1
    #print("NB CONFLITS", c_index, len(conflits))
    #print(label_conflits)
    #print("REDUCE CONFLITS MATRIX")

    ordered_labels = []
    ic = 0
    for c in conflits:
        #print("CONFLIT :", ic)
        l = c[0]
        ordered_labels.append(l)
        l1 = c[1]
        for k in label_conflits[l]:
            if k > ic:
                lc = conflits[k]
                lc0=lc[0]
                lc1=lc[1]
                if lc[0] == l:
                    lc = copy.deepcopy((l1,lc1))
                else:
                    lc = copy.deepcopy((lc0,l1))
        ic = ic + 1

    independant_labels = []
    new_labels = {}
    for l in labels:
        if l not in ordered_labels:
            independant_labels.append(l)
            new_labels[l] = l

    #print("REDUCED CONFLITS", conflits)
    #print("DEPENDANT LABELS", ordered_labels)
    #print("INDEPENDANT LABELS", independant_labels)
    nc = len(conflits)
    for i in range(nc):
        c = conflits[nc - i - 1]
        new_labels[c[0]] = new_labels[c[1]]
    #print("NEW LABELS", new_labels)
    return new_labels

def gauss_elimination(A):
    r = -1
    j = 0
    while j < min(A.shape[1], A.shape[0]):
        # Chercher le maximum d'une colonne
        max_el = A[j, j]
        max_row = j
        for k in range(j + 1, A.shape[0]):
            if A[k, j] > max_el:
                max_el = A[k, j]
                max_row = k

        if A[max_row, j] != 0:
            r += 1
            # Division par le pivot
            for i in range(A.shape[1]):
                A[max_row, i] = A[max_row, i] // max_el

            # Permuter la ligne courante avec la ligne comprenant le max
            if max_row != r:
                tmp = np.copy(A[max_row, :])
                A[max_row, :] = A[r, :]
                A[r, :] = tmp
            # Mettre toutes les autres colonnes à 0
            for i in range(j, A.shape[0]):
                if i != r:
                    A[i, :] -= A[i, j] * A[r, :]
        j += 1



def Gauss_elimination(A, j, r, max_el, max_row):
        for k in range(j + 1, A.shape[0]):
            if A[k, j] > max_el:
                max_el = A[k, j]
                max_row = k

        if A[max_row, j] != 0:
            r += 1
            # Division par le pivot
            for i in range(A.shape[1]):
                if max_el != 0:
                    A[max_row, i] = A[max_row, i] // max_el

            # Permuter la ligne courante avec la ligne comprenant le max
            if max_row != r:
                tmp = np.copy(A[max_row, :])
                A[max_row, :] = A[r, :]
                A[r, :] = tmp
            # Mettre toutes les autres colonnes à 0
            for i in range(j, A.shape[0]):
                if i != r:
                    A[i, :] -= A[i, j] * A[r, :]

def correct_conflicts(test):
    r = -1
    A = np.copy(test[1:test.shape[0], :])
    if A.shape[0] <= A.shape[1]:
        for j in range(min(A.shape[0], A.shape[1])):
            max_el = A[j, j]
            max_row = j
            if max_el != 0:
                Gauss_elimination(A, j, r, max_el, max_row)
                test[1:test.shape[0], :] = A
            else:
                for i in range(j+1, A.shape[1]):
                    if A[j, i] != 0:
                        tmp = test[:, j]
                        test[:, j] = test[:, i]
                        test[:, i] = tmp
                        break
                A = test[1:test.shape[0], :]
                Gauss_elimination(A, j, r, max_el, max_row)
                test[1:test.shape[0], :] = A


def tri_matrix(mat):
    cpt = 0
    for j in range(mat.shape[1]):
        if max(mat[1:mat.shape[0], j]) != 1 and min(mat[1:mat.shape[0], j]) != 0:
            cpt += 1
    independant_array = np.zeros((mat.shape[0], cpt), dtype=mat.dtype)
    array2 = np.zeros((mat.shape[0], mat.shape[1] - cpt), dtype=mat.dtype)
    k = 0
    l = 0
    for i in range(1, mat.shape[0]):
        for j in range(mat.shape[1]):
            if max(mat[1:mat.shape[0], j]) != 1 and min(mat[1:mat.shape[0], j]) != 0:
                if k < independant_array.shape[1]:
                    independant_array[:, k] = mat[:, j]
                    k += 1
            else:
                if l < array2.shape[1]:
                    array2[:, l] = mat[:, j]
                    l += 1
    res = np.concatenate((array2, independant_array), axis=1)
    return res


if __name__ == '__main__':
    img = np.random.randint(0, 2, (15, 15))
    conf_list = [(1, 28), (3, 29), (9, 30), (55, 32), (33, 55), (55, 82), (57, 84)]
    mat_test = np.array([[1, 2, 3], [1, 1, 1], [0, 0, 1]])
    mat, nc, nl = convert_list_to_matrix(conf_list)
    print("Matrice avant tri : \n", mat, nc, nl)
    conflicts_reduction(mat)
    print("RESULTAT : \n", mat)
    X = system_resolution(mat)
    print(X)

    t0 = time.process_time()
    resolve_labels_conflits(conf_list)
    t1 = time.process_time() - t0
    print("TIME VERSION OPTIMISEE :", t1)

"""
def gauss2(A):
 h = 0#ligne du pivot
 k = 0  #Colonne du pivot
 while h < A.shape[0] and k < A.shape[1]:
    print(h, k)
   # Trouver le k-ième pivot
    i_max = max([int(abs(A [i, k])) for i in range(h, A.shape[0]-1)])
    print(i_max)
    if A[i_max, k] != 0:
    #  permuter les lignes (h, i_max) Pour toutes les lignes situées sous le pivot
        if i_max != h:
            tmp = np.copy(A[i_max, :])
            A[i_max, :] = A[h, :]
            A[h, :] = tmp
        for i in range(h + 1, A.shape[0]-1):
            f = A[i, k] // A [h, k]
        # Remplir avec des zéros la partie inférieure de la colonne pivot
            A [i, k] = 0
        # Faites pour tous les éléments restants dans la ligne en cours
            for j in range(k + 1, A.shape[1]-1):
                A[i, j] = A[i,j] - A [h, j] * f
      # Augmenter la rangée et la colonne de pivot
        h = h + 1
 k = k + 1

"""
