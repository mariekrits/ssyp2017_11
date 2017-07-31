import Utils
import numpy as np


def zhang_suen(image, w, h):
    def iteration(step=1):
        pixels_to_change = []
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if image[i][j] == 255:
                    continue
                seq = [Utils.bin_px(image[i - 1][j]),
                       Utils.bin_px(image[i - 1][j + 1]),
                       Utils.bin_px(image[i][j + 1]),
                       Utils.bin_px(image[i + 1][j + 1]),
                       Utils.bin_px(image[i + 1][j]),
                       Utils.bin_px(image[i + 1][j - 1]),
                       Utils.bin_px(image[i][j - 1]),
                       Utils.bin_px(image[i - 1][j - 1]),
                       Utils.bin_px(image[i - 1][j])]
                cond = [False for _ in range(4)]
                cond[0] = (2 <= sum(seq[:-1]) <= 6)
                cond[1] = (''.join([str(x) for x in seq]).count('01') == 1)
                if step == 1:
                    cond[2] = (seq[0] * seq[2] * seq[4] == 0)
                    cond[3] = (seq[2] * seq[4] * seq[6] == 0)
                else:
                    cond[2] = (seq[0] * seq[2] * seq[6] == 0)
                    cond[3] = (seq[0] * seq[4] * seq[6] == 0)
                if all(cond):
                    pixels_to_change.append((i, j))
        for (_i, _j) in pixels_to_change:
            image[_i][_j] = 255
        return len(pixels_to_change)

    c = 0
    while True:
        c += 1
        #print("Iteration", c)
        pixels_count = iteration()
        pixels_count += iteration(step=2)
        if pixels_count == 0:
            break


def wu_tsai(image, w, h):
    # всего - 14 таблиц (a-n),
    # 0 - белый пиксель (=0),
    # 1 - чёрный пиксель (=1),
    # 2 - текущий пиксель (=c),
    # 3 - хотя бы один из них должен быть белым (=y),
    # 4 - ничего не значащий пиксель (=x)

    tables = [np.array([]) for _ in range(14)]

    def init_tables():
        tables[0] = np.array([
            [1, 1, 3],
            [1, 2, 0],
            [1, 1, 3]]
        )
        tables[1] = np.array([
            [1, 1, 1],
            [1, 2, 1],
            [3, 0, 3]]
        )
        tables[2] = np.array([
            [3, 1, 1, 4],
            [0, 2, 1, 1],
            [3, 1, 1, 4]]
        )
        tables[3] = np.array([
            [3, 0, 3],
            [1, 2, 1],
            [1, 1, 1],
            [4, 1, 4]]
        )
        tables[4] = np.array([
            [4, 0, 0],
            [1, 2, 0],
            [4, 1, 4]]
        )
        tables[5] = np.array([
            [4, 1, 1],
            [0, 2, 1],
            [0, 0, 4]]
        )
        tables[6] = np.array([
            [0, 1, 0],
            [0, 2, 1],
            [0, 0, 0]]
        )
        tables[7] = np.array([
            [4, 1, 4],
            [1, 2, 0],
            [4, 0, 0]]
        )
        tables[8] = np.array([
            [0, 0, 4],
            [0, 2, 1],
            [4, 1, 1]]
        )
        tables[9] = np.array([
            [0, 0, 0],
            [0, 2, 1],
            [0, 1, 0]]
        )
        tables[10] = np.array([
            [0, 0, 0],
            [0, 2, 0],
            [1, 1, 1]]
        )
        tables[11] = np.array([
            [1, 0, 0],
            [1, 2, 0],
            [1, 0, 0]]
        )
        tables[12] = np.array([
            [1, 1, 1],
            [0, 2, 0],
            [0, 0, 0]]
        )
        tables[13] = np.array([
            [0, 0, 1],
            [0, 2, 1],
            [0, 0, 1]]
        )

    def comp_tables(arr, pattern):
        white_px_flag = False
        for _i in range(arr.shape[0]):
            for _j in range(arr.shape[1]):
                if pattern[_i][_j] == 0 and arr[_i][_j] != 0:
                    return False
                if pattern[_i][_j] == 1 and arr[_i][_j] != 1:
                    return False
                if pattern[_i][_j] == 2 or pattern[_i][_j] == 4:
                    continue
                if pattern[_i][_j] == 3 and arr[_i][_j] == 0:
                    white_px_flag = True
        return pattern[pattern == 3].size == 0 or white_px_flag

    init_tables()
    vec_func = np.vectorize(Utils.bin_px)
    flag = True
    while flag:
        flag = False
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if image[i][j] == 255:
                    continue
                res = False
                for _table in tables[:2] + tables[4:]:
                    res |= comp_tables(vec_func(image[i - 1:i + 2, j - 1:j + 2]), _table)
                if j < w - 2:
                    res |= comp_tables(vec_func(image[i - 1:i + 2, j - 1:j + 3]), tables[2])
                if i < h - 2:
                    res |= comp_tables(vec_func(image[i - 1:i + 3, j - 1:j + 2]), tables[3])
                if res:
                    flag = True
                    image[i][j] = 255


def thinning(image, w, h):
    #print('Step 1 done!')
    #Utils.save_debug_img(image, 'images/step1.png')
    zhang_suen(image, w, h)
    #print('Step 2 done!')
    #Utils.save_debug_img(image, 'images/step2.png')
    wu_tsai(image, w, h)
    #print('Step 3 done!')
    #Utils.save_debug_img(image, 'images/step3.png')
