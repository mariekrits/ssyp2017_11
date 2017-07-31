import numpy as np
from numpy.linalg import eig, inv

# points = np.array([[0, 3.], [2., 2], [2., -2], [0., -3], [-2., 2]]) +
# conicPoints = np.array([[-3, 0.], [-2., 2], [2., 2], [3., 0], [2., -2]])
# points = np.array([[-3, 6.], [-2., 2], [1., -1], [4., 2], [3., 7]]) +
#conicPoints = np.array([[-2.5, -1.], [-1.5, -1.5], [0., -1.5], [0.5, -1], [-3., -0.5]])
#conicPoints = np.array([[14., 17], [15., 17], [16., 17], [22., 7], [22., 8]])
conicPoints = np.array([[19., 21], [20., 18], [20., 15], [21., 12], [21., 10]])


class Ellipse:
    A = None
    B = None
    C = None
    D = None
    E = None
    F = None
    a = None
    b = None
    x0 = None
    y0 = None
    Theta = None
    majorAxis = None

    def __init__(self, points, F=1.0):
        self.A, self.B, self.C, self.D, self.E, self.F = self.fivePointsToConic(points, F)
        self.x0, self.y0, self.Theta, self.a, self.b, self.majorAxis =\
            self.toCanonicalParameters(self.A, self.B, self.C, self.D, self.E, self.F)

    def fivePointsToConic(self, points, f=1.0):
        from numpy.linalg import lstsq

        x = points[:, 0]
        y = points[:, 1]
        if max(x.shape) < 5:
            raise ValueError('Need >= 5 points to solve for conic section')

        A = np.vstack([x**2, x * y, y**2, x, y]).T
        fullSolution = lstsq(A, f * np.ones(x.size))
        (a, b, c, d, e) = fullSolution[0]

        return (a, b, c, d, e, f)

    def fitEllipse(self, points):
        x = points[:, :1]
        y = points[:, 1:2]
        D = np.hstack((x * x, x * y, y * y, x, y, np.ones_like(x)))
        S = np.dot(D.T, D)
        C = np.zeros([6, 6])
        C[0, 2] = C[2, 0] = 2;
        C[1, 1] = -1
        E, V = eig(np.dot(inv(S), C))
        n = np.argmax(np.abs(E))
        a = V[:, n]
        return a

    def toCanonicalParameters(self, a, b, c, d, e, f):
        k1 = (c * d - b * e / 2) / (b * b / 2 - 2 * a * c)
        k2 = (a * e - b * d / 2) / (b * b / 2 - 2 * a * c)
        mmm = 1/(a * k1 * k1 + b * k1 * k2 + c * k2 * k2 + f)
        m11 = a / (a * k1 * k1 + b * k1 * k2 + c * k2 * k2 + f)
        m12 = (b / 2) / (a * k1 * k1 + b * k1 * k2 + c * k2 * k2 + f)
        m22 = c / (a * k1 * k1 + b * k1 * k2 + c * k2 * k2 + f)
        L1 = ((m11 + m22) + np.sqrt((m11 - m22) ** 2 + 4 * m12 * m12)) / 2
        L2 = ((m11 + m22) - np.sqrt((m11 - m22) ** 2 + 4 * m12 * m12)) / 2
        if m11 < m22: #a==major
            semimajor = 1 / np.sqrt(np.abs(L2))
            semiminor = 1 / np.sqrt(np.abs(L1))
            U1 = -L1 + m11
            U2 = m12
        else: #a==minor
            semimajor = 1 / np.sqrt(np.abs(L1))
            semiminor = 1 / np.sqrt(np.abs(L2))
            U1 = L1 - m22
            U2 = m12
        T = np.arccos(U1/np.sqrt(U1 ** 2 + U2 ** 2))

        return np.round(k1, 4), np.round(k2, 4), T, np.round(semimajor, 4), np.round(semiminor, 4), (U1, U2)

    def intersectWithLine(self, La, Lb, Lc):
        alpha = La * self.a * np.cos(self.Theta) + self.a * Lb * np.sin(self.Theta)
        beta = Lb * self.b * np.cos(self.Theta) - La * self.b * np.sin(self.Theta)
        gamma = La * self.x0 + Lb * self.y0 + Lc
        det = beta ** 2 + (-gamma ** 2 + alpha ** 2)
        delta1 = (beta + np.sqrt(det)) / ((alpha - gamma))
        delta2 = (beta - np.sqrt(det)) / ((alpha - gamma))
        t1 = np.arctan(delta1) / np.pi
        t2 = np.arctan(delta2) / np.pi
        t1 = t1 if t1 > 0 else t1 + 1
        t2 = t2 if t2 > 0 else t2 + 1
        return t1, t2

    def getPlot(self, count=1000):
        Ts = np.linspace(0.,1., count, endpoint=False)
        Xs = [self.a * np.cos(2 * np.pi * t) * np.cos(self.Theta) - self.b * np.sin(2 * np.pi * t) * np.sin(self.Theta) + self.x0 for t in Ts]
        Ys = [self.a * np.cos(2 * np.pi * t) * np.sin(self.Theta) + self.b * np.sin(2 * np.pi * t) * np.cos(self.Theta) + self.y0 for t in Ts]
        return Xs, Ys

    def getPointByParamater(self, t):
        X = self.a * np.cos(2 * np.pi * t) * np.cos(self.Theta) - self.b * np.sin(2 * np.pi * t) * np.sin(self.Theta) + self.x0
        Y = self.a * np.cos(2 * np.pi * t) * np.sin(self.Theta) + self.b * np.sin(2 * np.pi * t) * np.cos(self.Theta) + self.y0
        return X, Y


def fitEllipse(points):
    x = points[:, :1]
    y = points[:, 1:2]
    D =  np.hstack((x*x, x*y, y*y, x, y, np.ones_like(x)))
    S = np.dot(D.T,D)
    C = np.zeros([6,6])
    C[0,2] = C[2,0] = 2; C[1,1] = -1
    E, V =  eig(np.dot(inv(S), C))
    n = np.argmax(np.abs(E))
    a = V[:,n]
    return a


def ellipse_center(a):
    b,c,d,f,g,a = a[1]/2, a[2], a[3]/2, a[4]/2, a[5], a[0]
    num = b*b-a*c
    x0=(c*d-b*f)/num
    y0=(a*f-b*d)/num
    return np.array([x0,y0])


def ellipse_angle_of_rotation( a ):
    b,c,d,f,g,a = a[1]/2, a[2], a[3]/2, a[4]/2, a[5], a[0]
    return 0.5*np.arctan(2*b/(a-c))


def ellipse_axis_length( a ):
    b,c,d,f,g,a = a[1]/2, a[2], a[3]/2, a[4]/2, a[5], a[0]
    up = 2*(a*f*f+c*d*d+g*b*b-2*b*d*f-a*c*g)
    down1=(b*b-a*c)*( (c-a)*np.sqrt(1+4*b*b/((a-c)*(a-c)))-(c+a))
    down2=(b*b-a*c)*( (a-c)*np.sqrt(1+4*b*b/((a-c)*(a-c)))-(c+a))
    res1=np.sqrt(np.abs(up/down1))
    res2=np.sqrt(np.abs(up/down2))
    return np.array([res1, res2])


def ellipse_angle_of_rotation2( a ):
    b,c,d,f,g,a = a[1]/2, a[2], a[3]/2, a[4]/2, a[5], a[0]
    if b == 0:
        if a > c:
            return 0
        else:
            return np.pi/2
    else:
        if a > c:
            return np.arctan(2*b/(a-c))/2
        else:
            return np.pi/2 + np.arctan(2*b/(a-c))/2