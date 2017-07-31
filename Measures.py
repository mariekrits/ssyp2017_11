import numpy as np


def VectorEuclidianLength(a):
    return np.sqrt(sum(map(lambda x: x**2, a)))


def MinkowskiMeasure(a, b, p):
    if len(a) != len(b) or (p < 1 and p > 0):
        raise ValueError("Лол кек чебурек")
    return sum([np.float_power(a[i]-b[i],p) for i in range(len(a))])


def EuclidianMeasure(a, b):
    return MinkowskiMeasure(a, b, 2)


def CountingMeasure(a, b):
    return MinkowskiMeasure(a, b, 0)


def CosineMeasure(a, b):
    if len(a) != len(b):
        raise ValueError("SOSNOOLEY")
    dotProd = np.dot(a, b)
    cosine = dotProd / (VectorEuclidianLength(a) * VectorEuclidianLength(b))
    return np.arccos(cosine)