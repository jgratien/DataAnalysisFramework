import numpy as np
import ctypes as ct
import os
from sys import platform

# Load dll into memory
ARRAYPARTLIB = None

_DIRNAME = os.path.dirname(os.path.abspath(__file__));
if platform == "linux" or platform == "linux2":
    # Linux
    filename = os.path.join(_DIRNAME, "libarray_part.so")
    print(filename)
    ARRAYPARTLIB = ct.cdll.LoadLibrary(filename)
elif platform == "win32":
    # Windows...
    ARRAYPARTLIB = ct.cdll.LoadLibrary(os.path.join(_DIRNAME, "array_part.dll"))


class partition(ct.Structure):
    _fields_ = [("idx", ct.c_int),
                ("nx", ct.c_int),
                ("ny", ct.c_int),
                ("nz", ct.c_int),
                ("array", ct.POINTER(ct.c_float))]


class partitions(ct.Structure):
    _fields_ = [("n_parts", ct.c_int),
                ("parts", ct.POINTER(partition))]


ARRAYPARTLIB.array_split_band.argtypes = [np.ctypeslib.ndpointer(dtype=np.float32),
                                          ct.c_int, ct.c_int, ct.c_long, ct.c_int]

# return type
ARRAYPARTLIB.array_split_band.restype = ct.POINTER(partitions)


ARRAYPARTLIB.free_partitions.argtypes = [ct.POINTER(partitions)]
ARRAYPARTLIB.free_partitions.restype = ct.c_void_p


# bind method to a python method
def array_split_band(cube, n_part):
    p_tab = ARRAYPARTLIB.array_split_band(cube, cube.shape[2], cube.shape[1], cube.shape[0], n_part)

    p_nz = int(cube.shape[0]/n_part + 1)

    result = []
    partitions = p_tab.contents.parts
    for i in range(p_tab.contents.n_parts):
        values = np.array(np.fromiter(partitions[i].array, dtype=np.float32, count=partitions[i].nx*partitions[i].ny*partitions[i].nz*2))
        values = np.reshape(values, newshape=[2, p_nz, cube.shape[1], cube.shape[2]])
        result.append({"idx": partitions[i].idx, "array": values})

    ARRAYPARTLIB.free_partitions(p_tab)

    return result


if __name__ == '__main__':
    cube = np.array( np.arange(0, 120) + .5, dtype=np.float32)
    cube = np.reshape(cube, newshape=[8, 3, 5])
    print(cube)
    result = array_split_band(cube, 8)
    print(result)
