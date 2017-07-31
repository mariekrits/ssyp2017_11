from Ellipse import *
import matplotlib.pyplot as plt
import numpy as np
def PlotModel(segments, arcs, keyPoints, lines, intersections, width=30, height=30):
    plt.close()
    plt.grid()
    for arc in arcs:
        R = None
        if arc['zeroArc']:
            R = np.arange(2 * np.pi * (arc['t2'] - 1), 2 * np.pi * arc['t1'], 0.01)
        else:
            R = np.arange(2 * np.pi * arc['t1'], 2 * np.pi * arc['t2'], 0.01)
        x = arc['a'] * np.cos(R) * np.cos(arc['theta']) - arc['b'] * np.sin(R) * np.sin(arc['theta']) + arc['x0']
        y = arc['a'] * np.cos(R) * np.sin(arc['theta']) + arc['b'] * np.sin(R) * np.cos(arc['theta']) + arc['y0']
        plt.plot(x, y, color='green')
    for segment in segments:
        A_ = segment[0][1] - segment[1][1]
        B_ = segment[1][0] - segment[0][0]
        C_ = segment[0][0]*segment[1][1] - segment[0][1]*segment[1][0]
        if B_ != 0:
            maxX = np.maximum(segment[0][0], segment[1][0])
            minX = np.minimum(segment[0][0], segment[1][0])
            Line = np.linspace(minX, maxX, num=1000)
            LYs = [(-C_ - A_ * t) / B_ for t in Line]
            plt.plot(Line, LYs, linestyle='-', color='black')
        else:
            maxY = np.maximum(segment[0][1], segment[1][1])
            minY = np.minimum(segment[0][1], segment[1][1])
            Line = np.linspace(minY, maxY, num=1000)
            LXs = [-C_/A_ for t in Line]
            plt.plot(LXs, Line, linestyle='-', color='black')
    for line in lines:
        if line['B'] != 0:
            Line = np.linspace(0, width, num=1000)
            LYs = [(-line['C'] - line['A'] * t) / line['B'] for t in Line]
            plt.plot(Line, LYs, linestyle=':', color='magenta')
        else:
            Line = np.linspace(0, height, num=1000)
            LXs = [-line['C']/line['A'] for t in Line]
            plt.plot(LXs, Line, linestyle=':', color='magenta')

    plt.plot([point[0] for point in keyPoints], [point[1] for point in keyPoints], marker='o', linestyle='none', markerfacecolor='red')
    plt.plot([point[0] for point in intersections], [point[1] for point in intersections], marker='8', linestyle='none', markerfacecolor='blue')
    plt.show()

'''arc = 2
R = np.arange(0,arc*np.pi, 0.01)

a = fitEllipse(conicPoints)
ell = a[:]
center = ellipse_center(a)
phi = ellipse_angle_of_rotation(a)
a, b = ellipse_axis_length(a)

xx = center[0] + a*np.cos(R)*np.cos(phi) - b*np.sin(R)*np.sin(phi)
yy = center[1] + a*np.cos(R)*np.sin(phi) + b*np.sin(R)*np.cos(phi)

elll = Ellipse(np.array([[xx[t], yy[t]] for t in range(5)]), F=0.993572993298)
plt.grid()
plt.plot(*elll.getPlot())
plt.plot(conicPoints[:,:1], conicPoints[:,1:2])
plt.show()'''

#PlotModel([[(13,16),(13,19)]], [{'a':a, 'b':b, 'x0':center[0], 'y0':center[1], 'theta':phi, 't1':t1, 't2':t2, 'zeroArc':False}], [(16, 15), (16, 17)], [{'A':1, 'B':0, 'C':-18}], [(12, 17),(13, 15)])