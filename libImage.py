from PIL import Image
import numpy as np
import random
from matplotlib import image
import scipy.misc
import threading
from numpy.linalg import eig, inv
import os
import pickle
from symcutter import cut_symbols
WHITE = 255
BLACK = 0
GREY = 100
X = 2
Y = 3
C = 2


def color(p):
    for i in range(len(p)):
        if p[i] == 255:
            p[i] = 0
        else:
            p[i] = 1
    return p


def color2(p, w, h):
    for i in range(h):
        for j in range(w):
            if p[i, j] == 255:
                p[i, j] = 0
            else:
                p[i, j] = 1
    return p


def check_tables(tbl, piece, need_mod):
    ys = 0
    ones = 0
    matches = 0
    havey = False
    for c in range(len(tbl)):
        if tbl[c] == X:
            continue
        if tbl[c] == Y:
            ys += 1
            havey = True
            continue
        if tbl[c] != piece[c]:
            ones += 1
        else:
            ones += 1
            matches += 1
    if (ones == matches) and ((not havey) or (ys > 0)):
        need_mod = True
        return need_mod
    return need_mod


def skeleton1(pixels, w, h):
    print("Начало 1 стадии скелетизации")
    was_mod = [True, True]
    iterat = 1
    while was_mod[0] or was_mod[1]:
        mod = pixels.__deepcopy__(pixels)
        was_mod[iterat % 2] = False
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if pixels[i, j] == WHITE:
                    continue
                piece = color(
                    [pixels[i - 1, j], pixels[i - 1, j + 1], pixels[i, j + 1], pixels[i + 1, j + 1], pixels[i + 1, j],
                     pixels[i + 1, j - 1], pixels[i, j - 1], pixels[i - 1, j - 1]])
                st1 = (sum(piece))
                if st1 > 6 or st1 < 2:
                    continue
                a = "".join([str(x) for x in piece])
                a += str(piece[0])
                if a.count("01") != 1:
                    continue
                if iterat % 2 == 1:
                    if piece[0] == 1 and piece[2] == 1 and piece[4] == 1:
                        continue
                    if piece[2] == 1 and piece[4] == 1 and piece[6] == 1:
                        continue
                if iterat % 2 == 0:
                    if piece[0] == 1 and piece[2] == 1 and piece[6] == 1:
                        continue
                    if piece[0] == 1 and piece[4] == 1 and piece[6] == 1:
                        continue
                mod[i, j] = WHITE
                was_mod[iterat % 2] = True
        pixels = mod
        print(iterat)
        iterat += 1
    print("Готово")
    return pixels


def skeleton2(pixels, w, h):
    print("Начало 2 стадии скелетизации")
    was_mod = True
    iterat = 1
    while was_mod:
        was_mod = False
        tables = [
            [1, Y, 0, Y, 1, 1, 1, 1],
            [1, 1, 1, Y, 0, Y, 1, 1],
            [1, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, X, 1, X, 1, X],
            [1, X, 0, 0, 0, X, 1, X],
            [1, 1, 1, X, 0, 0, 0, X],
            [0, X, 1, 1, 1, X, 0, 0],
            [0, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 1, 1],
            [0, 0, 0, 1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 1],
            [0, 1, 1, 1, 0, 0, 0, 0]
        ]
        table43 = [Y, 1, 1, X, 0, 1, 1, Y, 1, 1, X]
        table34 = [Y, 0, Y, 1, 1, 1, 1, 1, X, 1, X]
        for i in range(1, h - 2):
            for j in range(1, w - 2):
                if pixels[i, j] == WHITE:
                    continue
                need_mod = False
                piece3x3 = color([pixels[i - 1, j], pixels[i - 1, j + 1], pixels[i, j + 1], pixels[i + 1, j + 1],
                                  pixels[i + 1, j], pixels[i + 1, j - 1], pixels[i, j - 1], pixels[i - 1, j - 1]])
                piece43 = color([pixels[i - 1, j - 1], pixels[i - 1, j], pixels[i - 1, j + 1], pixels[i - 1, j + 2],
                                 pixels[i, j - 1], pixels[i, j + 1], pixels[i, j + 2], pixels[i + 1, j - 1],
                                 pixels[i + 1, j], pixels[i + 1, j + 1], pixels[i + 1, j + 2]])
                piece34 = color([pixels[i - 1, j - 1], pixels[i - 1, j], pixels[i - 1, j + 1], pixels[i, j - 1],
                                 pixels[i, j + 1], pixels[i + 1, j - 1], pixels[i + 1, j], pixels[i + 1, j + 1],
                                 pixels[i + 2, j - 1], pixels[i + 2, j], pixels[i + 2, j + 1]])
                for tbl in tables:
                    need_mod = check_tables(tbl, piece3x3, need_mod)
                need_mod = check_tables(table43, piece43, need_mod)
                need_mod = check_tables(table34, piece34, need_mod)
                if need_mod:
                    was_mod = True
                    pixels[i, j] = WHITE
        print(iterat)
        iterat += 1
    print("Готово")
    return pixels


def key1(pixels, w, h):
    print("Выделение ключевых точек", end="")
    keypix = [[WHITE for _ in range(w)] for __ in range(h)]
    keypix = np.array(keypix)
    pxls = color2(pixels.__deepcopy__(pixels), w, h)
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            if pxls[i, j] == 0:
                continue
            if sum([pxls[i - 1, j], pxls[i - 1, j + 1], pxls[i, j + 1], pxls[i + 1, j + 1], pxls[i + 1, j],
                    pxls[i + 1, j - 1], pxls[i, j - 1], pxls[i - 1, j - 1]]) != 2:
                keypix[i, j] = BLACK
                continue
            # a group
            if pxls[i - 1, j + 1] == 1 and pxls[i + 1, j + 1] == 1:
                keypix[i, j] = BLACK
                continue
            if pxls[i + 1, j - 1] == 1 and pxls[i + 1, j + 1] == 1:
                keypix[i, j] = BLACK
                continue
            if pxls[i - 1, j - 1] == 1 and pxls[i + 1, j - 1] == 1:
                keypix[i, j] = BLACK
                continue
            if pxls[i - 1, j - 1] == 1 and pxls[i - 1, j + 1] == 1:
                keypix[i, j] = BLACK
                continue
            # b group
            if (pxls[i - 1, j] == 1 and pxls[i + 1, j + 1] == 1) and (pxls[i, j + 2] == 1 or pxls[i + 1, j + 2] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i + 1, j - 1] == 1 and pxls[i, j + 1] == 1) and (pxls[i - 2, j - 1] == 1 or pxls[i - 2, j] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i - 1, j] == 1 and pxls[i + 1, j - 1] == 1) and (pxls[i, j - 2] == 1 or pxls[i + 1, j - 2] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i - 1, j + 1] == 1 and pxls[i + 1, j] == 1) and (pxls[i - 1, j + 2] == 1 or pxls[i, j + 2] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i - 1, j - 1] == 1 and pxls[i, j + 1] == 1) and (pxls[i - 2, j - 1] == 1 or pxls[i - 2, j] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i, j - 1] == 1 and pxls[i - 1, j + 1] == 1) and (pxls[i - 2, j] == 1 or pxls[i - 2, j + 1] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i - 1, j - 1] == 1 and pxls[i + 1, j] == 1) and (pxls[i - 1, j - 2] == 1 or pxls[i, j - 2] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i, j - 1] == 1 and pxls[i + 1, j + 1] == 1) and (pxls[i + 2, j] == 1 or pxls[i + 2, j + 1] == 1):
                keypix[i, j] = BLACK
                continue
            # y group
            if (pxls[i - 1, j - 1] == 1 and pxls[i + 1, j + 1] == 1) and (pxls[i - 2, j] == 1 or pxls[i, j - 2] == 1)\
                    and (pxls[i, j + 2] == 1 or pxls[i + 2, j] == 1):
                keypix[i, j] = BLACK
                continue
            if (pxls[i - 1, j + 1] == 1 and pxls[i + 1, j - 1] == 1) and (pxls[i + 2, j] == 1 or pxls[i, j - 2] == 1)\
                    and (pxls[i, j + 2] == 1 or pxls[i - 2, j] == 1):
                keypix[i, j] = BLACK
                continue
    print("...OK")
    return keypix


def key2(pixels, w, h):
    print("Объединение ключевых точек", end="")
    was_mod = True
    #modded = pixels.__deepcopy__(pixels)
    while was_mod:
        was_mod = False
        to_mod = []
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if pixels[i, j] == WHITE:
                    continue
                piece = color([pixels[i - 1, j], pixels[i - 1, j + 1], pixels[i, j + 1], pixels[i + 1, j + 1],
                               pixels[i + 1, j], pixels[i + 1, j - 1], pixels[i, j - 1], pixels[i - 1, j - 1],
                               pixels[i - 1, j]])
                coords_piece = [[i - 1, j], [i - 1, j + 1], [i, j + 1], [i + 1, j + 1],
                               [i + 1, j], [i + 1, j - 1], [i, j - 1], [i - 1, j - 1],
                               [i - 1, j]]
                a = "".join([str(x) for x in piece])
                matches = 0
                keys = 0
                for pnt in coords_piece:
                    if pixels[pnt[0], pnt[1]] == 0:
                        keys +=1
                    if pnt in to_mod:
                        matches += 1
                if keys == matches:
                    continue
                if a.count("01") == 1:
                    to_mod.append([i, j])
                    was_mod = True
        for point in to_mod:
            pixels[point[0], point[1]] = WHITE
    print("...OK")
    return pixels


def find_black(arr, i, j, ):
    temp = []
    if arr[i - 1, j] != 0:
        temp.append((i - 1, j))
    if arr[i - 1, j + 1] != 0:
        temp.append((i - 1, j + 1))
    if arr[i, j + 1] != 0:
        temp.append((i, j + 1))
    if arr[i + 1, j + 1] != 0:
        temp.append((i + 1, j + 1))
    if arr[i + 1, j] != 0:
        temp.append((i + 1, j))
    if arr[i + 1, j - 1] != 0:
        temp.append((i + 1, j - 1))
    if arr[i, j - 1] != 0:
        temp.append((i, j - 1))
    if arr[i - 1, j - 1] != 0:
        temp.append((i - 1, j - 1))
    return temp


def find_line(arr, line, it=0, delete=False, cmp=[False]):
    i, j = line[-1]
    neigh = find_black(arr, i, j)
    if delete:
        if arr[i, j] == 3:
            cmp[0] = True
            arr[i, j] = 1
        elif arr[neigh[0]] == 3:
            arr[neigh[0]] = 1
            cmp[0] = True
        elif arr[neigh[1]] == 3:
            arr[neigh[1]] = 1
            cmp[0] = True
    for n in neigh:
        if arr[n] > 1 and it > 0:
            line.append(n)
            return line
    it += 1
    if arr[i, j] != 1:
        return line
    else:
        if neigh[0] == line[-2]:
            line.append(neigh[1])
            line = find_line(arr, line, it, delete=delete, cmp=cmp)
        else:
            line.append(neigh[0])
            line = find_line(arr, line, it, delete=delete, cmp=cmp)
    return line


def find_vectors(line):
    vectors = []
    for it in range(1, len(line)):
        i = line[it][0] - line[0][0]
        j = line[it][1] - line[0][1]
        vectors.append((i, j))
    return vectors


def calculate_vectors(vectors):
    crt = [0, 0]
    for it in range(len(vectors)):
        i = vectors[it][0]
        j = vectors[it][1]
        crt[0] += i * (2 ** (-it))
        crt[1] += j * (2 ** (-it))

    return tuple(crt)


def separate_key_pix(pixels, keypix, w, h):
    print("Поиск точек изгиба:")
    allarr = np.copy(color2(pixels, w, h))
    kp = color2(keypix, w, h)
    for i in range(h):
        for j in range(w):
            allarr[i, j] += kp[i, j]
    for i in range(h):
        for j in range(w):
            if allarr[i, j] != 2:
                continue
            piece = [pixels[i - 1, j], pixels[i - 1, j + 1], pixels[i, j + 1], pixels[i + 1, j + 1], pixels[i + 1, j],
                     pixels[i + 1, j - 1], pixels[i, j - 1], pixels[i - 1, j - 1]]
            if sum(piece) == 2:
                allarr[i, j] += 1

    for i in range(h):
        for j in range(w):
            if allarr[i, j] != 3:
                continue
            line = [[], []]
            vector = []
            final_vector = []
            neigh = find_black(allarr, i, j)
            # TODO Запилить FOR
            line[0].append((i, j))
            line[0].append(neigh[0])
            line[1].append((i, j))
            line[1].append(neigh[1])
            line[0] = find_line(allarr, line[0])
            line[1] = find_line(allarr, line[1])
            vector.append(find_vectors(line[0]))
            vector.append(find_vectors(line[1]))
            final_vector.append(calculate_vectors(vector[0]))
            final_vector.append(calculate_vectors(vector[1]))
            print(final_vector)
            m = final_vector[0][0]
            n = final_vector[0][1]
            k = final_vector[1][0]
            l = final_vector[1][1]
            cs = ((m * k) + (n * l)) / ((np.sqrt((m ** 2) + (n ** 2))) * (np.sqrt((m ** 2) + (n ** 2))))
            angle = np.arccos(cs)
            angle = np.rad2deg(angle)
            print(angle)
            if angle < 120:
                allarr[i, j] = 2
    print("Готово")
    return allarr


def open_image(filename):
    w, h = 0, 0
    pixels = None
    with Image.open(filename).convert("L") as img:
        img = Image.open(filename).convert("L")
        w, h = img.size
        print("Разрешение " + str(w) + "*" + str(h) + " пикселей")
        pixels = img.load()
        pixels = np.reshape([pixels[i, j] for j in range(h) for i in range(w)], (h, w))
    return pixels, w, h


def creategist(pixels, w, h):
    gist = [0 for _ in range(256)]
    for j in range(w):
        for i in range(h):
            gist[pixels[i, j]] += 1
    return gist


def binarize(pixels, gist):
    print("Начало бинаризации", end='')
    n = sum(gist)
    m = sum([t * gist[t] for t in range(256)])
    res = 0
    index = 0
    b = 0
    a = 0
    for i in range(0, 256):
        b += gist[i]
        a += i * gist[i]
        if b == 0 or n == b:
            continue
        v1 = b / n
        v2 = 1 - v1
        m1 = a / b
        m2 = (m - a) / (n - b)
        temp = v1 * v2 * ((m1 - m2) ** 2)
        if temp > res:
            res = temp
            index = i
    pixels[pixels >= index] = 255
    pixels[pixels < index] = 0
    print("...OK")
    return pixels, index


def calculateedges(allarr, w, h):
    tempallarr = allarr.__deepcopy__(allarr)
    listlines = []
    todo = []
    done = []
    for i in range(h):
        for j in range(w):
            if tempallarr[i, j] != 2:
                continue
            neigh = find_black(tempallarr, i, j)
            for n in neigh:
                if allarr[n[0], n[1]] == 1:
                    todo.append([(i, j), n])
            while len(todo) > 0:
                if todo[-1][1] in done:
                    todo.pop()
                    continue
                line = {"coords": [todo[-1][0], todo[-1][1]], "vectors": [], "cf": 0, "composite": False}
                cmp = [False]
                # TODO delete was true in next line
                line["coords"] = find_line(tempallarr, line["coords"], cmp=cmp)
                line["composite"] = cmp[0]
                todo.pop()
                done.append(line["coords"][1])
                done.append(line["coords"][-2])
                current = (line["coords"][-1][0], line["coords"][-1][1])
                neigh = find_black(tempallarr.__deepcopy__(tempallarr), current[0], current[1])
                for n in neigh:
                    if (not(n in done)) and (allarr[n[0], n[1]] == 1):
                        todo.append((current, n))
                length = 0
                for it in range(1, len(line["coords"])):
                    if (line["coords"][it][0] != line["coords"][it - 1][0]) and (line["coords"][it][1] !=
                                                                                 line["coords"][it - 1][1]):
                        length += np.sqrt(2)
                    else:
                        length += 1
                line["length"] = length
                line["eulength"] = np.sqrt(((line["coords"][0][0] - line["coords"][-1][0]) ** 2) +
                                           ((line["coords"][0][1] - line["coords"][-1][1]) ** 2))
                line["cf"] = length / line["eulength"]
                vectors = [find_vectors(line["coords"]), find_vectors(line["coords"][::-1])]
                line["vectors"].append(calculate_vectors(vectors[0]))
                line["vectors"].append(calculate_vectors(vectors[1]))
                listlines.append(line)
    return listlines


def calculate_triangles(lines, directs, image_vector):
    iter = 0
    for line in lines:
        iter += 1
        #if line["cf"] >= 1.1:
            #continue
        c = line["eulength"]
        len_ = line["length"]
        a_vector = line["vectors"][0]
        c_vector = ((line["coords"][-1][0] - line["coords"][0][0]), (line["coords"][-1][1] - line["coords"][0][1]))
        cs = ((a_vector[0] * c_vector[0]) + (a_vector[1] * c_vector[1])) / (np.sqrt((a_vector[0] ** 2) + (a_vector[1] ** 2)) * (np.sqrt(c_vector[0] ** 2) + (c_vector[1] ** 2)))
        a = ((c ** 2) - (len_ ** 2)) / (2 * ((c * cs) - len_))
        b = len_ - a
        csb = a_vector[0] / np.sqrt((a_vector[0] ** 2) + (a_vector[1] ** 2))
        dx = a * csb
        dy = a * np.sin(np.arccos(csb))
        point = (line["coords"][0][0] + dx, line["coords"][0][1] + dy)
        for iterat in range(len(directs)):
            image_vector[iterat] += calculate_lines_lines(directs[iterat][0], directs[iterat][1], directs[iterat][2], [line["coords"][0], point], [point, line["coords"][-1]])
    return image_vector


def calculate_lines_lines(A, B, C, a, b):
    to_return = 0
    segments = [a, b]
    for sgmt in segments:
        num1 = (A * sgmt[0][0]) + (B * sgmt[0][1]) + C
        num2 = (A * sgmt[1][0]) + (B * sgmt[1][1]) + C
        if (num1 == 0) or (num2 == 0):
            to_return += 1
            continue
        if (num1 > 0) != (num2 > 0):
            to_return += 1
    return to_return


def calculate_ellipses(lines, directs, image_vector):
    for line in lines:
        if line["cf"] < 1.1:
            continue
        D_ = []
        leng = len(line["coords"]) - 1
        for iter in range(5):
            point = (line["coords"][int((leng / 4) * iter)])
            print(point)
            D_.append([point[0] ** 2, point[0] * point[1], point[1] ** 2, point[0], point[1], 1])
        D_ = np.array(D_)
        S_ = np.dot(D_.T, D_)
        C_ = [
            [0, 0, 2, 0, 0, 0],
            [0, -1, 0, 0, 0, 0],
            [2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0]
        ]
        E_, V_ = eig(np.dot(inv(S_), C_))
        vector = V_[:,np.argmax(np.abs(E_))]
        A = vector[0]
        B = vector[1]
        C = vector[2]
        D = vector[3]
        E = vector[4]
        F = vector[5]
        x0 = ((C * D) - ((B * E) / 2)) / (((B ** 2) / 2) - (2 * A * C))
        y0 = ((A * E) - ((B * D) / 2)) / (((B ** 2) / 2) - (2 * A * C))
        M = 1 / ((A * (x0 ** 2)) + (B * x0 * y0) + (C * (y0 ** 2)) - F)
        m11 = A * M
        m22 = C * M
        m12 = (B * M) / 2
        lmb1 = (m11 + m22 + np.sqrt(((m11 - m22) ** 2) + 4 * (m12 ** 2))) / 2
        lmb2 = (m11 + m22 - np.sqrt(((m11 - m22) ** 2) + 4 * (m12 ** 2))) / 2
        if m11 < m22:
            U = (-lmb1 + m11, m12)
            a = 1 / np.sqrt(lmb2)
            b = 1 / np.sqrt(lmb1)
        else:
            U = (lmb1 - m22, m12)
            a = 1 / np.sqrt(lmb1)
            b = 1 / np.sqrt(lmb2)
        teta = np.arccos(U[0] / np.sqrt((U[0] ** 2) + (U[1] ** 2)))
        print(a, b, x0, y0, teta)
        for iterat in range(len(directs)):
            image_vector[iterat] += calculate_ellipse_line(directs[iterat][0], directs[iterat][1], directs[iterat][2], x0, y0, a, b, teta, line["coords"][0], line["coords"][-1], line["coords"][int(len(line["coords"]) / 2)])
    return image_vector


def calculate_ellipse_line(A, B, C, x0, y0, a, b, teta, point1, point2, point3):
    # point1 - edge start; point2 - edge end; point3 - point on the edge
    alf = ((A * a * np.cos(teta)) + (a * B * np.sin(teta)))
    bet = ((B * b * np.cos(teta)) - (A * b * np.sin(teta)))
    gam = ((A * x0) + (B * y0) + (C))
    d = [0, 0]
    t34 = [0, 0]
    if (bet ** 2) - (gam ** 2) + (alf ** 2) < 0:
        return 0
    d[0] = (bet + np.sqrt((bet ** 2) - (gam ** 2) + (alf ** 2))) / (alf - gam)
    d[1] = (bet - np.sqrt((bet ** 2) - (gam ** 2) + (alf ** 2))) / (alf - gam)
    for iterat in range(2):
        t34[iterat] = np.arctan(d[iterat]) / np.pi if np.arctan(d[iterat]) >= 0 else np.arctan(d[iterat]) / np.pi + 1
    cfA = point1[1] - point2[1]
    cfB = point2[0] - point1[0]
    cfC = (point1[0] * point2[1]) - (point2[0] * point1[1])
    xt0 = a * np.cos(teta) + x0
    yt0 = a * np.sin(teta) + y0
    point_t0 = (xt0, yt0)
    nums = [(cfA * xt0) + (cfB * yt0) + cfC, (cfA * point3[0]) + (cfB * point3[1]) + cfC]
    alf = ((cfA * a * np.cos(teta)) + (a * cfB * np.sin(teta)))
    bet = ((cfB * b * np.cos(teta)) - (cfA * b * np.sin(teta)))
    gam = ((cfA * x0) + (cfB * y0) + (cfC))
    d = [0, 0]
    t12 = [0, 0]
    d[0] = (bet + np.sqrt((bet ** 2) - (gam ** 2) + (alf ** 2))) / (alf - gam)
    d[1] = (bet - np.sqrt((bet ** 2) - (gam ** 2) + (alf ** 2))) / (alf - gam)
    for iterat in range(2):
        t12[iterat] = np.arctan(d[iterat]) / np.pi if np.arctan(d[iterat]) >= 0 else np.arctan(d[iterat]) / np.pi + 1
    to_return = 0
    if (nums[0] < 0) == (nums[1] < 0):
        if ((t34[0] >= 0) and (t34[0] <= t12[0])) or ((t34[0] >= t12[1]) and (t34[0] <= 1)):
            to_return += 1
        if ((t34[1] >= 0) and (t34[1] <= t12[0])) or ((t34[1] >= t12[1]) and (t34[1] <= 1)):
            to_return += 1
    else:
        if (t34[0] >= t12[0]) and (t34[0] <= t12[1]):
            to_return += 1
        if (t34[1] >= t12[0]) and (t34[1] <= t12[1]):
            to_return += 1
    if (t34[0] == t34[1]) and (to_return > 0):
        return 1
    else:
        return to_return


def process_one_image(filename, debug=False):
    pixels, w, h = open_image(filename)
    directs = []
    for iterat in range(5, 100, 3):
        directs.append([1, 0, int(-(h / 100) * iterat)])
    for iterat in range(5, 100, 3):
        directs.append([0, 1, int(-(w / 100) * iterat)])
    gist = creategist(pixels, w, h)
    pixels, index = binarize(pixels, gist)
    if debug:
        image.imsave("/home/ilya/картинки/debug/black.png", pixels, 0, 255, cmap="gray", origin="upper")
    w = len(pixels[0])
    h = len(pixels)
    pixels = skeleton1(pixels, w, h)
    if debug:
        image.imsave("/home/ilya/картинки/debug/skelet1.png", pixels, 0, 255, cmap="gray", origin="upper")
    pixels = skeleton2(pixels, w, h)
    if debug:
        image.imsave("/home/ilya/картинки/debug/skelet2.png", pixels, 0, 255, cmap="gray", origin="upper")
    keypix = key1(pixels, w, h)
    if debug:
        image.imsave("/home/ilya/картинки/debug/key1.png", keypix, 0, 255, cmap="gray", origin="upper")
    #keypix = key2(keypix, w, h)
    #if debug:
        #image.imsave("/home/ilya/картинки/debug/key2.png", keypix, 0, 255, cmap="gray", origin="upper")
    #allarr = separate_key_pix(pixels, keypix, w, h)
    allarr = np.copy(color2(pixels, w, h))
    for i in range(h):
        for j in range(w):
            if keypix[i, j] == 0:
                allarr[i, j] += 1
    if debug:
        rgb = [[0 for _ in range(w)] for __ in range(h)]
        for i in range(h):
            for j in range(w):
                if allarr[i][j] == 1:
                    rgb[i][j] = [0, 0, 0]
                elif allarr[i][j] == 2:
                    rgb[i][j] = [0, 255, 0]
                elif allarr[i][j] == 3:
                    rgb[i][j] = [255, 0, 0]
                else:
                    rgb[i][j] = [255, 255, 255]
        scipy.misc.toimage(rgb, cmin=0, cmax=255).save("/home/ilya/картинки/debug/key3.png")
    listlines = calculateedges(allarr, w, h)
    if debug:
        for ln in listlines:
            colors = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
            for crds in ln["coords"]:
                if rgb[crds[0]][crds[1]] == [0, 0, 0]:
                    rgb[crds[0]][crds[1]] = colors
        scipy.misc.toimage(rgb, cmin=0, cmax=255).save("/home/ilya/картинки/debug/edge.png")
    image_vector = [0 for _ in range(len(directs))]
    image_vector = calculate_triangles(listlines, directs, image_vector)
    #image_vectors.append(calculate_triangles(listlines, directs, image_vector))
    return image_vector


def process_image(filename, debug=False):
    uncut, w, h = open_image(filename)
    directs = []
    for iterat in range(5, 100, 4):
        directs.append([1, 0, int(-(h / 100) * iterat)])
    for iterat in range(5, 100, 4):
        directs.append([0, 1, int(-(w / 100) * iterat)])
    gist = creategist(uncut, w, h)
    uncut, index = binarize(uncut, gist)
    if debug:
        image.imsave("/home/ilya/картинки/debug/black.png", uncut, 0, 255, cmap="gray", origin="upper")
    images = cut_symbols(uncut, w, h)
    image_vectors = []
    for pixels in images:
        w = len(pixels[0])
        h = len(pixels)
        pixels = skeleton1(pixels, w, h)
        if debug:
            image.imsave("/home/ilya/картинки/debug/skelet1.png", pixels, 0, 255, cmap="gray", origin="upper")
        pixels = skeleton2(pixels, w, h)
        if debug:
            image.imsave("/home/ilya/картинки/debug/skelet2.png", pixels, 0, 255, cmap="gray", origin="upper")
        keypix = key1(pixels, w, h)
        if debug:
            image.imsave("/home/ilya/картинки/debug/key1.png", keypix, 0, 255, cmap="gray", origin="upper")
        #keypix = key2(keypix, w, h)
        #if debug:
            #image.imsave("/home/ilya/картинки/debug/key2.png", keypix, 0, 255, cmap="gray", origin="upper")
        #allarr = separate_key_pix(pixels, keypix, w, h)
        allarr = np.copy(color2(pixels, w, h))
        for i in range(h):
            for j in range(w):
                if keypix[i, j] == 0:
                    allarr[i, j] += 1
        if debug:
            rgb = [[0 for _ in range(w)] for __ in range(h)]
            for i in range(h):
                for j in range(w):
                    if allarr[i][j] == 1:
                        rgb[i][j] = [0, 0, 0]
                    elif allarr[i][j] == 2:
                        rgb[i][j] = [0, 255, 0]
                    elif allarr[i][j] == 3:
                        rgb[i][j] = [255, 0, 0]
                    else:
                        rgb[i][j] = [255, 255, 255]
            scipy.misc.toimage(rgb, cmin=0, cmax=255).save("/home/ilya/картинки/debug/key3.png")
        listlines = calculateedges(allarr, w, h)
        if debug:
            for ln in listlines:
                colors = (random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
                for crds in ln["coords"]:
                    if rgb[crds[0]][crds[1]] == [0, 0, 0]:
                        rgb[crds[0]][crds[1]] = colors
            scipy.misc.toimage(rgb, cmin=0, cmax=255).save("/home/ilya/картинки/debug/edge.png")
        image_vector = [0 for _ in range(len(directs))]
        image_vector = calculate_triangles(listlines, directs, image_vector)
        #image_vector = calculate_ellipses(listlines, directs, image_vector)
        image_vectors.append(image_vector)
    return image_vectors


def calculate_samples(sigset, sigout, recalc):
    root_dir = os.getcwd()
    try:
        if not (os.path.isfile("sample_vector") and (not recalc)):
            raise Exception
        fl = open("sample_vector","rb")
        print("yes file")
        sav = pickle.load(fl)
        fl.close()
    except:
        print("no file")
        fl = open("sample_vector", "wb")
        os.chdir("./samples")
        symboldirs = os.listdir()
        sample_vectors = {}
        symbols_count = len(symboldirs)
        iterat = 0
        for symdir in symboldirs:
            sigset.emit((100 / symbols_count) * iterat, symdir)
            samples = os.listdir("./" + symdir)
            sample_vectors[symdir] = []
            for sample in samples:
                print("samples/" + symdir + "/" + sample)
                try:
                    sv = process_image(symdir + "/" + sample)
                except:
                    print("Ошибка")
                else:
                    sample_vectors[symdir].append(sv[0])
            iterat += 1
        pickle.dump(sample_vectors, fl)
        sigset.emit(100, "Готов")
        fl.close
    else:
        sample_vectors = sav
    os.chdir(root_dir)
    print(sample_vectors)
    sigout.emit(sample_vectors)
    return  sample_vectors


def do_all(filename, sigset, sigout, sample_vectors):
    sigset.emit(0, "Распознавание")
    os.system("rm /home/ilya/картинки/debug/*")
    output = ""
    #cut_symbols(filename)
    image_vectors = process_image(filename, debug=True)
    numbers = {}
    for image_vector in image_vectors:
        j = 9999
        to_out = ""
        for key, symbol in sample_vectors.items():
            i = 9999
            print(key)
            print("\t", end="")
            for sample in symbol:
                sm = 0
                for iterat in range(len(sample)):
                    sm += (sample[iterat] - image_vector[iterat]) ** 2
                print(sm, end=" ")
                if sm < i:
                    i = sm
            if i < j:
                j = i
                to_out = key
            print("")
        print(to_out)
        print(image_vector)
        output += to_out
    sigout.emit(output)
    return 0
