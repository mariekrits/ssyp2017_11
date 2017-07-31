import numpy as np
import sympy as sp

def in_interval(num, interval):
    for i in interval:
        if i[0] <= num <= i[1]:
            return True
    return False

class MyEllipsis:
    def __init__(self, coefficients):
        self.coefficients = coefficients
        self.A, self.B, self.C, self.D, self.E, self.F = coefficients
        self.x0 = (self.C * self.D - self.B * self.E / 2) / (self.B ** 2 / 2 - 2 * self.A * self.C)
        self.y0 = (self.A * self.E - self.B * self.D / 2) / (self.B ** 2 / 2 - 2 * self.A * self.C)
        μ = 1 / (self.A * self.x0 ** 2 + self.B * self.x0 * self.y0 + self.C * self.y0 ** 2 + self.F)
        m11 = μ * self.A
        m22 = μ * self.C
        m12 = μ * self.B / 2
        λ1 = (m11 + m22 + sp.sqrt((m11 - m22) ** 2 + (4 * m12) ** 2)) / 2
        λ2 = (m11 + m22 - sp.sqrt((m11 - m22) ** 2 + (4 * m12) ** 2)) / 2
        if m11 < m22:
            U = (-λ1 + m11, m12)
            self.a = 1 / sp.sqrt(λ2)
            self.b = 1 / sp.sqrt(λ1)
        else:
            U = (λ1 - m22, m12)
            self.a = 1 / sp.sqrt(λ1)
            self.b = 1 / sp.sqrt(λ2)
        # print("U is:", U)
        self.Θ = np.arccos(float(U[0]) / np.sqrt(float(U[0] ** 2 + U[1] ** 2)))

    def get_xy_by_t(self, t):
        x = self.a * np.cos(2 * np.pi * t) * np.cos(self.Θ) - self.b * np.sin(2 * np.pi * t) * np.sin(self.Θ) + self.x0
        y = self.a * np.cos(2 * np.pi * t) * np.sin(self.Θ) - self.b * np.sin(2 * np.pi * t) * np.cos(self.Θ) + self.y0
        return x, y

    def get_t_by_line(self, A, B, C):
        # print(A, B, C)
        α = self.a * (A * np.cos(self.Θ) + B * np.sin(self.Θ))
        β = self.b * (B * np.cos(self.Θ) - A * np.sin(self.Θ))
        γ = A * self.x0 + B * self.y0 + C
        if β ** 2 - γ ** 2 + α ** 2 >= 0:
            δ1 = (β + sp.sqrt(β ** 2 - γ ** 2 + α ** 2)) / (α - γ)
            δ2 = (β - sp.sqrt(β ** 2 - γ ** 2 + α ** 2)) / (α - γ)
            # print(δ1, δ2)
            # print(type(δ1), type(δ2))
            t1 = np.arctan(np.float32(δ1)) / np.pi
            t2 = np.arctan(np.float32(δ2)) / np.pi
            return t1, t2

    def set_interval(self, xy1, xy2, xy_n):
        self.xy1 = xy1
        self.xy2 = xy2
        A, B, C = Line(0, xy1, xy2).get_coeff()
        t1, t2 = self.get_t_by_line(A, B, C)
        xt_0, yt_0 = self.get_xy_by_t(0)
        xt_n, yt_n = xy_n
        a = A * xt_0 + B * yt_0 + C
        b = A * xt_n + B * yt_n + C
        if np.sign(a) == np.sign(b):
            self.zeroarc = True
            self.interval = [(0, min(t1, t2)), (max(t1, t2), 1)]
        else:
            self.zeroarc = False
            self.interval = [(min(t1, t2), max(t1, t2))]

    def crossings(self, A, B, C):
        α = self.a * (A * np.cos(self.Θ) + B * np.sin(self.Θ))
        β = self.b * (B * np.cos(self.Θ) - A * np.sin(self.Θ))
        γ = A * self.x0 + B * self.y0 + C
        discr = β ** 2 + (α ** 2 - γ ** 2)
        if discr < 0:
            return 0
        elif discr == 0:
            δ = β / (α - γ)
            t = np.arctan(δ) / np.pi
            if in_interval(t, self.interval):
                return 1
            return 0
        else:
            δ1 = (β + sp.sqrt(β ** 2 - γ ** 2 + α ** 2)) / (α - γ)
            δ2 = (β - sp.sqrt(β ** 2 - γ ** 2 + α ** 2)) / (α - γ)
            t1 = np.arctan(np.float32(δ1)) / np.pi
            t2 = np.arctan(np.float32(δ2)) / np.pi
            k = 0
            if in_interval(t1, self.interval):
                k += 1
            if in_interval(t2, self.interval):
                k += 1
            return k

    def as_dict(self):
        line = Line(0, xy1=self.xy1, xy2=self.xy2)
        t = self.get_t_by_line(line.A, line.B, line.C)
        return {'a': self.a, 'b': self.b, 't1': min(t), 't2': max(t), 'x0': self.x0,
                'y0': self.y0, 'theta': self.Θ, 'zeroArc': self.zeroarc}


class Line:
    def __init__(self, flag, xy1=None, xy2=None, A=None, B=None, C=None):
        if flag == 0:
            x1, y1 = xy1
            x2, y2 = xy2
            self.B = x2 - x1
            self.A = (y1 - y2)
            self.C = (x1 * y2 - x2 * y1)
        else:
            self.B = B
            self.A = A
            self.C = C

    def as_dict(self):
        return {'A': self.A, 'B': self.B, 'C': self.C}

    def get_coeff(self):
        return self.A, self.B, self.C

    def on_line(self, xy):
        return self.A * xy[0] + self.B * xy[1] + self.C == 0

    def __str__(self):
        return "{} * x + {} * y + {} = 0".format(self.A, self.B, self.C)
