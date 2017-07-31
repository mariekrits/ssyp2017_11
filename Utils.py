from matplotlib import image
import numpy as np

def checkIntersectionBetweenLineAndSegment(L1, L2, M1, M2):
    def multiply(a, b):
        return a[0] * b[1] - a[1] * b[0]
    LL12 = (L2[0] - L1[0], L2[1] - L1[1])
    LM11 = (M1[0] - L1[0], M1[1] - L1[1])
    LM12 = (M2[0] - L1[0], M2[1] - L1[1])
    return True if multiply(LL12, LM11) * multiply(LL12, LM12) <= 0 else False


def save_debug_img(arr, filename):
    image.imsave(filename, arr, vmin=0, vmax=255, cmap='gray', origin='upper')


def print_img(arr):
    for x in arr:
        for p in x:
            print(p, end='')
        print()
    print()


def bin_px(px):
    return 0 if px == 255 else 1


def draw_image_by_xy(filename, dots, w, h):
    arr = np.zeros((h, w), dtype=np.int32)
    arr[arr == 0] = 255
    for dot in dots:
        arr[dot[0]][dot[1]] = 0
    save_debug_img(arr, filename)


def convert_bin_to_img(img):
    tmp_img = np.copy(img)
    for i in range(len(tmp_img)):
        for j in range(len(tmp_img[i])):
            tmp_img[i][j] = 0 if tmp_img[i][j] == 1 else 255
    return tmp_img


def matrix_by_xy(xy, h, w):
    arr = np.zeros((h, w), dtype=np.int32)
    for i in xy:
        arr[i[0], i[1]] = 1
    return arr


def xy_from_matrix(matrix, h, w):
    xy = []
    for i in range(h):
        for j in range(w):
            if matrix[i, j] == 1:
                xy.append((i, j))
    return xy