from PIL import Image
from matplotlib import image
import numpy as np
import os


def save_img(filename, pixels):
    image.imsave(filename, pixels, vmin=0, vmax=255, cmap="gray", origin='upper')

def convert_to_01(px):
    if px == 255:
        return 0
    return 1

def cut_symbols(pixels, w, h):
    #cwdir = os.getcwd()
    to_return = []
    #os.chdir("/tmp")
    '''img = Image.open(filename).convert('L')
    w, h = img.size
    pixels=img.load()
    pixels=np.reshape([pixels[i, j] for j in range(h) for i in range(w)], (h, w))
    hist = [0 for x in range(256)]
    for i in pixels:
        for j in i:
            hist[j] += 1

    m = 0
    n = 0
    for i in range(256):
        m += hist[i] * i
        n += hist[i]
    a = 0
    b = 0
    max_hist = 0
    max_i = 0
    for j in range(1, 256) :
        a += hist[j] * j
        b += hist[j]
        if b == 0 :
            continue
        v1 = b/n
        v2 = 1 - v1
        n1 = a/b
        n2 = (m-a)/(n-b)
        vn = v1*v2*(n2 - n1)**2
        if max_hist < vn :
            max_hist = vn
            max_i = j

    pixels[pixels >= max_i] = 255
    pixels[pixels < max_i] = 0
    

    image.imsave(filename + "1", pixels, vmin=0, vmax=255, cmap="gray", origin='upper')'''
    simb = []
    line = []
    count = 0
    count1 = 0
    for i in range(h):
        for j in range(w):
            if pixels[i, j] == 0:
                count += 1
        if w > count > 0 and len(line) % 2 == 0:
            line.append(i)
            # for j in range(w):
            #    pixels[i, j] = 0
        elif count == 0 and len(line) % 2 != 0 or count == w and len(line) % 2 != 0 :
            for j in range(w):
                if pixels[i - 1 , j] == 0 :
                    count1 += 1
            if count1 == 0 :
                line.append(i)
            count1 = 0
             # for j in range(w):
             #   pixels[i - 1, j] = 0
        count = 0
    for i in range(0, len(line), 2):
        tpm_1 = pixels[line[i] - 1 : line[i+1] + 1, 0: w]
        image.imsave("/tmp/line" + str(i//2) + ".png", tpm_1, vmin=0, vmax=255, cmap="gray", origin='upper')

    for a in range(len(line) // 2):
        print(a)
        img = Image.open('/tmp/line' + str(a) +'.png').convert('L')
        w, h = img.size
        tmp_1 = img.load()
        tmp_1 = np.reshape([tmp_1[i, j] for j in range(h) for i in range(w)], (h, w))
        simb.clear()
        for j in range(w):
            for i in range(h):
                if tmp_1[i, j] == 0:
                    count += 1
            if count > 0 and len(simb) % 2 == 0:
                simb.append(j)
            elif count == 0 and len(simb) % 2 != 0:
                simb.append(j - 1)
            count = 0
        for i in range(0, len(simb), 2):
            tmp_2 = list(tmp_1[0: h, simb[i] - 1: simb[i+1] + 2])
            # pixels = pixels[line[0] - 1: line[1] + 1, simb[0] - 1: simb[1] + 1]
            '''emps = [255 for _ in range(len(tmp_2[0]))]
            empss = []
            for iterat in range(int(len(tmp_2) * 0.17)):
                empss.append(emps)
            empss = np.array(empss)
            tmp_2 = np.concatenate((empss, tmp_2))
            tmp_2 = np.concatenate((tmp_2, empss))
            to_add = int((len(tmp_2) - len(tmp_2[0])) / 2)
            empre = np.array([255 for _ in range(to_add)])
            print(empre)
            tmp2 = []
            for iterat in range(len(tmp_2)):
                temp = np.concatenate((empre, tmp_2[iterat]))
                tmp2.append(np.concatenate((temp, empre)))'''
            image.imsave("/tmp/simbol" + str(a) + "." + str(i//2) + ".png", np.array(tmp_2), vmin=0, vmax=255, cmap="gray", origin='upper')
            to_return.append(np.array(tmp_2))
    #os.chdir(cwdir)
    #print(os.getcwd())
    return to_return

