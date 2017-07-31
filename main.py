from PIL import Image
import Binarization
import Sceletonization
import Utils
import GraphUtils
import FeatureExtraction
import Comparison
import sys
import os
import pickle
import numpy as np
from MyEllipsis import *
# from Drawing import *
# from matplotlib import image

sys.setrecursionlimit(100000)

step = 3

def processImage(pixels):
    '''
    #filename = 'images/3_1.png'
    Image.open(filename)
    img = Image.open(filename).convert('L')
    '''
    h, w = pixels.shape
    '''
    pixels = img.load()
    pixels = np.reshape([pixels[i, j] for j in range(h) for i in range(w)], (h, w))
    '''

    '''БИНАРИЗАЦИЯ'''
    Binarization.binarize(pixels)
    # image.imsave('debug228.png', pixels, vmin=0, vmax=255, cmap="gray", origin='upper')

    '''СКЕЛЕТИЗАЦИЯ'''
    Sceletonization.thinning(pixels, w, h)

    '''ВЫДЕЛЕНИЕ КЛЮЧЕВЫХ ПИКСЕЛЕЙ'''
    keyPixels = FeatureExtraction.keyPixels(np.array([[Utils.bin_px(pixels[i,j]) for j in range(w)] for i in range(h)]), w, h)
    keyMatrix = Utils.matrix_by_xy(keyPixels, h, w)
    FeatureExtraction.reduceKeyPixelBlobs(keyPixels, keyMatrix) #TODO поменять на итерационный
    vectorPoints = []
    bendPixels = FeatureExtraction.computeBendPoints(pixels, keyPixels, vectorPoints)

    '''ПОСТРОЕНИЕ СОЕДИНИТЕЛЬНЫХ РЁБЕР'''
    k = 0
    for i in vectorPoints:
        k += 1

    blackPixels = Utils.xy_from_matrix(np.array([[Utils.bin_px(pixels[i,j]) for j in range(w)] for i in range(h)]), h, w)

    startPoints = keyPixels + bendPixels

    tempKeyPixels = []

    for i in GraphUtils.leeAlgorithm(startPoints, blackPixels):
        tempKeyPixels.append(list(map(lambda _: _.coord, i)))

    edges = []

    for i in tempKeyPixels:
        if not (i[::-1] in edges or i in edges):
            edges.append(i)

    r = 0
    for i in edges:
        r += 1

    # Ищем коэффициенты изгиба
    coefficient = []

    for i in edges:
        x1 = i[0][0]
        x2 = i[-1][0]
        y1 = i[0][1]
        y2 = i[-1][1]
        d = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        p = GraphUtils.fullLen(i) / d
        coefficient.append(p)

    vectors = []

    for i in range(len(edges)):
        vector = np.array((0., 0.))
        for t in range(len(edges[i]) - 1):
            j = np.array(edges[i][t])
            k = np.array(edges[i][t + 1])
            vector += (k - j) * 2 ** -t
        vectors.append(vector)

    '''ПОСТРОЕНИЕ МОДЕЛИ'''
    def threeInARow(points):
        for first in range(len(points) - 2):
            for last in range(2, len(points)):
                for mid in range(first + 1, last):
                    if Line(0, xy1=points[first], xy2=points[last]).on_line(points[mid]):
                        return True
        return False


    def intersection_line_segment(A, B, C, M1, M2):
        temp1 = A * M1[0] + B * M1[1] + C
        temp2 = A * M2[0] + B * M2[1] + C
        return temp1 * temp2 < 0

    def approximation(edges, vectors, i, P_list, S_list, O_list):
        O = edges[i][0]
        S = edges[i][-1]
        OM = vectors[i]
        OS = (S[0] - O[0], S[1] - O[1])
        c = np.sqrt((O[0] - S[0]) ** 2 + (O[1] - S[1]) ** 2)
        length = GraphUtils.fullLen(edges[i])
        cos_alpha = (OM[0] * OS[0] + OM[1] * OS[1]) / (
            np.sqrt(OM[0] ** 2 + OM[1] ** 2) * np.sqrt(OS[0] ** 2 + OS[1] ** 2))
        if cos_alpha != 1:
            a = (c ** 2 - length ** 2) / (2 * (c * cos_alpha - length))
            cos_beta = OM[0] / np.sqrt(OM[0] ** 2 + OM[1] ** 2)
            sin_beta = np.sqrt(1 - cos_beta ** 2)
            delta_x = a * cos_beta
            delta_y = a * sin_beta
            P = O[0] + delta_x, O[1] + delta_y
            OP = P[0] - O[0], P[1] - O[1]
            # С ОТРАЖЕНИЕМ
            if (OS[0] * OM[1] - OS[1] * OM[0]) * (OS[0] * OP[1] - OS[1] * OP[0]) >= 0:
                P_list.append(P)
                S_list.append(S)
                O_list.append(O)
            else:
                S_list.append(S)
                O_list.append(O)
                # TODO: отражение точки относительно отрезка
                temp_line = Line(0, xy1=O, xy2=S)
                A, B, C = temp_line.A, temp_line.B, temp_line.C
                first_matrix = np.array([[A, B], [B, -A]], dtype=np.float32)
                second_vector = np.array([-C, B * P[0] - A * P[1]], dtype=np.float32)
                x1, y1 = np.linalg.solve(first_matrix, second_vector)
                P = (2 * x1 - P[0], 2 * y1 - P[1])
                P_list.append(P)
        else:
            P_list.append(edges[i][len(edges[i]) // 2])
            O_list.append(O)
            S_list.append(S)


    def fivePointsToConic(points, f=1.0):
        from numpy.linalg import lstsq

        x = points[:, 0]
        y = points[:, 1]
        if max(x.shape) < 5:
            raise ValueError('Need >= 5 points to solve for conic section')

        A = np.vstack([x**2, x * y, y**2, x, y]).T
        fullSolution = lstsq(A, f * np.ones(x.size))
        (a, b, c, d, e) = fullSolution[0]

        return (a, b, c, d, e, f)

    P_list = []
    S_list = []
    O_list = []
    ellipses = []
    for i in range(len(edges)):
        # Геометрия
        if coefficient[i] >= 1.1 or len(edges[i]) < 5 or threeInARow(edges[i][:3] + edges[i][:-3:-1]):
            approximation(edges, vectors, i, P_list, S_list, O_list)
        # Эллипсы и матан
        else:
            if len(edges[i]) >= 5:
                vector_a = [edges[i][0], edges[i][len(edges[i]) // 4], edges[i][len(edges[i]) // 2],
                            edges[i][len(edges[i]) // 4 * 3], edges[i][-1]]
                try:
                    max_V = fivePointsToConic(np.array(vector_a))
                except:
                    print("shit")
                if max_V[1] ** 2 / 4 - max_V[0] * max_V[2] < 0:
                    ellipses.append(MyEllipsis(max_V))
                    ellipses[-1].set_interval(edges[i][0], edges[i][-1], edges[i][len(edges[i]) // 2])
                else:
                    approximation(edges, vectors, i, P_list, S_list, O_list)

    OPS_points = list(zip(O_list, P_list, S_list))

    # # print(key_pixels)

    #PlotModel(segments=segments, arcs=ellipses_dict, keyPoints=keyPixels,
    #         lines=lines_dict, intersections=[])

    '''ВЫДЕЛЕНИЕ ВЕКТОРА'''
    line = []
    featureVector = []
    x = step
    y = step
    while x < 100:
        line.append([Line(1, A=1, B=0, C=-(w/100)*x)])
        x += step
    while y < 100:
        line.append([Line(1, A=0, B=1, C=-(h/100)*y)])
        y += step

    for it in line:
        A, B, C = it[0].A, it[0].B, it[0].C
        it.append(0)
        featureVector.append(0)
        for ell in ellipses:
            crossings = ell.crossings(A, B, C)
            it[-1] += crossings
            featureVector[-1] += crossings
        for O, P, S in OPS_points:
            if intersection_line_segment(A, B, C, O, P):
                it[-1] += 1
                featureVector[-1] += 1
            if intersection_line_segment(A, B, C, P, S):
                it[-1] += 1
                featureVector[-1] += 1
    segments = [[O, P] for O, P, _ in OPS_points] + [[S, P] for _, P, S in OPS_points]

    ellipses_dict = list(map(lambda _: _.as_dict(), ellipses))
    lines_dict = list(map(lambda _: _[0].as_dict(), line))
    return featureVector

'''ПОЛУЧЕНИЕ ЭТАЛОНОВ'''
references = []


def calculateSamples(recalc=False):
    root_dir = os.getcwd()
    if os.path.isfile("sample_vector") and (not recalc):
        fl = open("sample_vector","rb")
        print("yes file")
        sample_vectors = pickle.load(fl)
        fl.close()
    else:
        print("no file")
        fl = open("sample_vector", "wb")
        os.chdir("./samples")
        symboldirs = os.listdir()
        symbols_count = len(symboldirs)
        sample_vectors = {}
        i = 0
        for symdir in symboldirs:
            samples = os.listdir("./" + symdir)
            sample_vectors[symdir] = []
            for sample in samples:
                print("samples/" + symdir + "/" + sample)
                try:
                    img = Image.open(symdir + "/" + sample).convert('L')
                    w, h = img.size
                    pixels = img.load()
                    pixels = np.reshape([pixels[i, j] for j in range(h) for i in range(w)], (h, w))
                    sv = processImage(pixels)
                except:
                    print("Ошибка")
                else:
                    if sum(sv) != 0:
                        sample_vectors[symdir].append(sv)
            i += 1
        pickle.dump(sample_vectors, fl)
        fl.close()
    os.chdir(root_dir)
    # print(sample_vectors)
    return  sample_vectors
#references = calculate_samples(True)
'''СРАВНЕНИЕ С ЭТАЛОНОМ'''
#filenames = ["images/0_1.png","images/1_1.png", "images/2_1.png", "images/3_1.png", "images/4_1.png", "images/5_1.png", "images/6_1.png", "images/7_1.png", "images/8_1.png", "images/9_1.png"]
#for filename in filenames:
#    print(filename)
#    print(Comparison.compareWithReferences(processImage(filename), references))
print('GG')

#TODO бинаризация DONE
#TODO скелетизация DONE
#TODO выделение ключевых пикселей DONE дополнительно проверить выделение изгибов
#TODO построение ребер DONE
#TODO построение модели DONE
#TODO выделение векторов DONE
#TODO получение эталонов DONE
#TODO сравнение с эталоном DONE затестить