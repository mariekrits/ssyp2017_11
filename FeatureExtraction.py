import numpy as np
import GraphUtils
import copy

def is_all_equal(col, indices, value):
    if col.count(value) != len(indices):
        return False
    for i in indices:
        if col[i] != value:
            return False
    return True


def is_alfa(nearest):
    for counter in range(4):
        if alfa_key(nearest, counter):
            return True
    return False


def alfa_key(nearest, num):
    if num == 0:
        return is_all_equal(nearest, (1, 3), 1)
    elif num == 1:
        return is_all_equal(nearest, (3, 5), 1)
    elif num == 2:
        return is_all_equal(nearest, (5, 7), 1)
    elif num == 3:
        return is_all_equal(nearest, (1, 7), 1)


def is_beta(nearest, binpix, i, j):
    for counter in range(8):
        if beta_key(nearest, binpix, i, j, counter):
            return True
    return False


def beta_key(nearest, binpix, i, j, num):
    if num == 0:
        return is_all_equal(nearest, (0, 3), 1) and binpix[i, j + 2] + binpix[i + 1, j + 2] >= 1
    elif num == 1:
        return is_all_equal(nearest, (0, 5), 1) and binpix[i, j - 2] + binpix[i + 1, j - 2] >= 1
    elif num == 2:
        return is_all_equal(nearest, (2, 5), 1) and binpix[i + 2, j] + binpix[i + 2, j - 1] >= 1
    elif num == 3:
        return is_all_equal(nearest, (1, 4), 1) and binpix[i, j + 2] + binpix[i - 1, j + 2] >= 1
    elif num == 4:
        return is_all_equal(nearest, (7, 2), 1) and binpix[i - 2, j] + binpix[i - 2, j - 1] >= 1
    elif num == 5:
        return is_all_equal(nearest, (7, 4), 1) and binpix[i, j - 2] + binpix[i - 1, j - 2] >= 1
    elif num == 6:
        return is_all_equal(nearest, (1, 6), 1) and binpix[i - 2, j] + binpix[i - 2, j + 1] >= 1
    elif num == 7:
        return is_all_equal(nearest, (3, 6), 1) and binpix[i + 2, j] + binpix[i + 2, j + 1] >= 1


def is_gamma(nearest, binpix, i, j):
    return (is_all_equal(nearest, (-1, 3), 1) and binpix[i + 2, j] + binpix[i, j + 2] >= 1 and
            binpix[i - 2, j] + binpix[i, j - 2] >= 1) or (
           is_all_equal(nearest, (1, -3), 1) and binpix[i - 2, j] + binpix[i, j + 2] >= 1 and
           binpix[i + 2, j] + binpix[i, j - 2] >= 1)


def keyPixels(bin_pixels, w, h):
    key_pixels = []

    for i in range(0, h):
        for j in range(0, w):
            if bin_pixels[i, j] == 1:
                if 2 <= i < h - 2 and 2 <= j < w - 2:
                    nearest = [bin_pixels[i - 1, j], bin_pixels[i - 1, j + 1], bin_pixels[i, j + 1],
                               bin_pixels[i + 1, j + 1], bin_pixels[i + 1, j], bin_pixels[i + 1, j - 1],
                               bin_pixels[i, j - 1], bin_pixels[i - 1, j - 1]]
                    if sum(nearest) != 2 or is_alfa(nearest) or is_beta(nearest, bin_pixels, i, j) or \
                            is_gamma(nearest, bin_pixels, i, j):
                        key_pixels.append((i, j))
                elif j == 0:
                    if i == 0 and bin_pixels[0, 1] + bin_pixels[1, 0] + bin_pixels[1, 1] != 2:
                        key_pixels.append((i, j))
                    elif i == h - 1 and bin_pixels[h - 1, 1] + bin_pixels[h - 2, 0] + bin_pixels[h - 2, 1] != 2:
                        key_pixels.append((i, j))
                    elif np.sum(bin_pixels[i - 1: i + 2, 0: 2]) - 1 != 2 or \
                                            bin_pixels[i + 1, 1] + bin_pixels[i - 1, 1] == 2 or \
                                                    bin_pixels[i - 1, 0] + bin_pixels[i + 1, 1] + bin_pixels[
                                        i, 2] == 3 or \
                                                    bin_pixels[i + 1, 0] + bin_pixels[i - 1, 1] + bin_pixels[i, 2] == 3:
                        key_pixels.append((i, j))
                elif j == w - 1:
                    if i == 0 and bin_pixels[0, w - 2] + bin_pixels[1, w - 2] + bin_pixels[1, w - 1] != 2:
                        key_pixels.append((i, j))
                    elif i == h - 1 and bin_pixels[h - 1, w - 2] + bin_pixels[h - 2, w - 1] + bin_pixels[
                                h - 2, w - 2] != 2:
                        key_pixels.append((i, j))
                    elif np.sum(bin_pixels[i - 1: i + 2, w - 2: w]) - 1 != 2 or bin_pixels[i + 1, w - 2] + bin_pixels[
                                i - 1, w - 2] == 2 or \
                                                    bin_pixels[i - 1, w - 1] + bin_pixels[i + 1, w - 2] + bin_pixels[
                                        i, w - 3] == 3 or \
                                                    bin_pixels[i + 1, w - 1] + bin_pixels[i - 1, w - 2] + bin_pixels[
                                        i, w - 3] == 3:
                        key_pixels.append((i, j))
                elif i == 0:
                    if np.sum(bin_pixels[0: 2, j - 1: j + 2]) - 1 != 2 or bin_pixels[1, j - 1] + \
                            bin_pixels[1, j + 1] == 2:
                        key_pixels.append((i, j))
                elif i == h - 1:
                    if np.sum(bin_pixels[h - 2: h, j - 1, j + 2]) - 1 != 2 or bin_pixels[h - 2, i - 1] + bin_pixels[
                                h - 2, i + 1]:
                        key_pixels.append((i, j))
                else:
                    nearest = [bin_pixels[i - 1, j], bin_pixels[i - 1, j + 1], bin_pixels[i, j + 1],
                               bin_pixels[i + 1, j + 1], bin_pixels[i + 1, j], bin_pixels[i + 1, j - 1],
                               bin_pixels[i, j - 1], bin_pixels[i - 1, j - 1]]
                    if np.sum(nearest) != 2:
                        key_pixels.append((i, j))
    return key_pixels


def reduceKeyPixelBlobs(keypixels, keymatrix):
    while True:
        flag = False
        for i, j in keypixels:
            if keymatrix[i, j] == 1:
                slc = [keymatrix[i - 1, j], keymatrix[i - 1, j + 1], keymatrix[i, j + 1],
                       keymatrix[i + 1, j + 1], keymatrix[i + 1, j], keymatrix[i + 1, j - 1],
                       keymatrix[i, j - 1], keymatrix[i - 1, j - 1]]

                string = ''.join(map(lambda _: str(_), slc)) + str(slc[0])
                oi = string.count('01')
                if oi == 1:
                    keypixels.remove((i, j))
                    keymatrix[i, j] = 0
                    flag = True
        if not flag:
            break

def computeBendPoints(pixels, keypixels, vectorpoints):
    temp_key_pixels = copy.deepcopy(keypixels)
    bend_pixels = []
    for i in keypixels:
        x = GraphUtils.vectorSearch(np.array(i), np.array(keypixels), pixels, is_start=True, vector_points=vectorpoints)
        if x is not None and len(x) != 0:
            # print(x)
            i1 = x[0][0]
            i2 = x[1][0]
            j1 = x[0][1]
            j2 = x[1][1]
            _cos = (i1 * i2 + j1 * j2) / (np.sqrt(i1 ** 2 + j1 ** 2) * np.sqrt(i2 ** 2 + j2 ** 2))
            tmp = np.arccos(float(_cos))
            angle = np.rad2deg(tmp)
            # print(angle)
            if angle >= 120:
                temp_key_pixels.remove(i)
                bend_pixels.append(i)
    keypixels = temp_key_pixels
    return bend_pixels