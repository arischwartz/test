from __future__ import division
import sys
import numpy as np
cimport numpy as np
from cython.parallel import prange

import SIPSimCpp

DTYPE = np.float
ctypedef np.float_t DTYPE_t

    
def add_diffusion(np.ndarray[DTYPE_t, ndim=2] arr, 
                  float T=298, float B=1.195e9, float G=7.87e-10, int M=882):
    """Adding diffusion to GC values and calculating BD.
    See Clay et al., 2003 for more details.
    Args:
    arr -- 2d-array: [[GC_value,],[frag_length,]]
    T -- gradient temperature in Kelvin
    B -- beta coefficient
    G -- G coefficient
    M -- molecular weight per pair base pair of dry cesium DNA
    Return:
    np.arr -- 1d numpy array of BD values
    """

    # bouyant density calc
    cdef int c1 = 100
    cdef double c2 = 0.098
    cdef double c3 = 1.66
    # calc
    cdef int n = len(arr[0])
    cdef double[:] out = np.empty(n, dtype=DTYPE)
    cdef unsigned int i
    cdef double diff = 0.0
    for i in xrange(n):
        diff = SIPSimCpp.calc_diffusion(arr[0,i], arr[1,i], T, B, G, M)
        out[i] = (arr[0,i] + diff) / c1 * c2 + c3
    return out


def add_incorp(frag_BD, incorp_func, double isotopeMaxBD):
    """Adding isotope incorporation BD-shift values to BD-0%-incorp
    values
    Args:
    incorp_func -- function that returns a 1d-list with a float
    isotopeMaxBD -- the max BD possible with the selected isotope 
    """    
    cdef int n = len(frag_BD)
    
    cdef int i = 0
    cdef double y = 100.0
    cdef double z = 0
    
    for i in xrange(n):
        z = incorp_func.sample()[0]
        frag_BD[i] += z / y * isotopeMaxBD



