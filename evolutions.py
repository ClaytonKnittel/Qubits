from extramath import spinor
from math import sin, cos, sinh, cosh


sx = spinor(spinor(0, 1), spinor(1, 0))
sy = spinor(spinor(0, 1j), spinor(-1j, 0))
sz = spinor(spinor(1, 0), spinor(0, -1))
identity = spinor(spinor(1, 0), spinor(0, 1))


def p(psi):
    return spinor(spinor(psi[0] * psi[0].conjugate(), psi[1] * psi[0].conjugate()),
                  spinor(psi[0] * psi[1].conjugate(), psi[1] * psi[1].conjugate()))


def commutator(a, b):
    return a * b - b * a

def neg_commutator(a, b):
    return a * b + b * a

def runge_kutta(funct, psi, t, dt):
    # function of form f(psi, t)
    k1 = funct(psi, t) * dt
    k2 = funct(psi + k1 / 2, t + dt / 2) * dt
    k3 = funct(psi + k2 / 2, t + dt / 2) * dt
    k4 = funct(psi + k3, t + dt) * dt
    return psi + (k1 + (k2 + k3) * 2 + k4) / 6


class Hamiltonian:

    def __init__(self, time_inde, time_dep=spinor(0, 0, 0, 0)):
        self.__i = time_inde
        self.__t = time_dep

    def eval(self, t):
        return self.__i + self.__t * t


class Psi:

    def psi(self):
        pass

    def next(self, t, dt):
        pass

    def __abs__(self):
        pass

    def __copy__(self):
        pass

    def x(self):
        pass

    def y(self):
        pass

    def z(self):
        pass

    def create_density(self):
        pass

    def vec(self):
        return [self.x(), self.y(), self.z()]


class _vecpsi(Psi):

    def __init__(self, psi):
        self.__psi = psi
        self.__density_matrix = None
        self.create_density()

    def psi(self):
        return self.__psi

    def set_psi(self, psi):
        self.__psi = psi

    def __abs__(self):
        return complex((self.__psi * self.__psi.conjugate()) ** .5).real

    def x(self):
        return complex((sx * self.__density_matrix).trace()).real

    def y(self):
        return complex((sy * self.__density_matrix).trace()).real

    def z(self):
        return complex((sz * self.__density_matrix).trace()).real

    def create_density(self):
        self.__density_matrix = p(self.__psi)


class _p(Psi):

    def __init__(self, psi):
        self.__p = p(psi)
        self.__psi = psi

    def p(self):
        return self.__p

    def psi(self):
        return self.__psi

    def set_psi(self, psi):
        self.__psi = psi
        self.__p = p(psi)

    def set_p(self, p):
        self.__p = p

    def __abs__(self):
        return self.__p.trace().real

    def x(self):
        return complex((self.__p * sx).trace()).real

    def y(self):
        return complex((self.__p * sy).trace()).real

    def z(self):
        return complex((self.__p * sz).trace()).real


class Schrodinger(_vecpsi):

    def __init__(self, psi, H):
        super().__init__(psi)
        if isinstance(H, Hamiltonian):
            self.__H = H
        else:
            self.__H = Hamiltonian(H)

    def __copy__(self):
        return Schrodinger(super().psi(), self.__H)

    @staticmethod
    def lab_frame_h(theta, phi, d1, d2, o1):
        return lambda t, psi: (sz * (cos(theta(t)) * d1 + d2)
                                             + sx * cos(theta(t)) * sin(phi(t)) * o1
                                             + sy * sin(theta(t)) * sin(phi(t)) * o1) * psi / 2

    @staticmethod
    def rot_frame_h(phi, detune, rabi):
        return lambda t, psi: (sz * detune(t) + (sx * cos(phi(t)) + sy * sin(phi(t))) * rabi(t)) * psi / 2

    def next(self, t, dt):
        super().set_psi(self.__runge_kutta(t, dt))
        return super().psi()

    def __euler(self, t, dt):
        psi = super().psi()
        return psi + self.__dpsi_dt(t, psi) * dt

    def __runge_kutta(self, t, dt):
        psi = super().psi()
        k1 = self.__dpsi_dt(t, psi) * dt
        k2 = self.__dpsi_dt(t + dt / 2, psi + k1 / 2) * dt
        k3 = self.__dpsi_dt(t + dt / 2, psi + k2 / 2) * dt
        k4 = self.__dpsi_dt(t + dt, psi + k3) * dt
        return psi + (k1 + k2 * 2 + k3 * 2 + k4) / 6

    def __dpsi_dt(self, t, psi):
        return self.__H.eval(t) * psi * -1j


class Exact(_vecpsi):

    # sxc, syc and szc are the coefficients in front of the three corresponding pauli matrices in the hamiltonian
    def __init__(self, psi, sxc, syc, szc):
        super().__init__(psi)
        self.__x = sxc
        self.__y = syc
        self.__z = szc
        self.__sum = (sxc ** 2 + syc ** 2 + szc ** 2) ** .5
        self.__mat = (sx * sxc + sy * syc + sz * szc) / self.__sum
        self.__time = 0
        self.__update()

    def __copy__(self):
        return Exact(super().psi(), self.__x, self.__y, self.__z)

    def psi(self):
        return self.__matrix * super().psi()

    def __update(self):
        self.__matrix = identity * cos(self.__sum * self.__time) - self.__mat * 1j * sin(self.__sum * self.__time)

    def next(self, t, dt):
        self.__time += dt
        self.__update()


class StochasticME(_p):

    def __init__(self, psi, H, gamma, L, J):
        super().__init__(psi)
        if isinstance(H, Hamiltonian):
            self.__H = H
        else:
            self.__H = Hamiltonian(H)
        self.__gamma = gamma
        self.__L = L
        self.__J = J

    def __copy__(self):
        return StochasticME(super().psi(), self.__H, self.__gamma, self.__L, self.__J)

    def lfunc(self, p):
        return self.__L * p * self.__L.h() - neg_commutator(self.__L.h() * self.__L, p) / 2

    def next(self, t, dt):
        self.set_p(runge_kutta(self.val_at, super().p(), t, dt))

    def val_at(self, p, t):
        a = commutator(self.__H.eval(t), p) * -1j
        b = self.lfunc(p) * self.__gamma
        return a + b


class StochasticMeasurement(_p):

    def __init__(self, psi, H, std_deviation, random=None):
        super().__init__(psi)
        self.__s = std_deviation
        if isinstance(H, Hamiltonian):
            self.__H = H
        else:
            self.__H = Hamiltonian(H)
        if random is None:
            from numpy import random as rand
            self.rand = rand
        else:
            self.rand = random
        self.__last_r = 0

    def __repr__(self):
        return '{' + str(super().x()) + ', ' + str(super().y()) + ', ' + str(super().z()) + '}'

    def __copy__(self):
        from numpy import random as ran
        ran.seed(self.rand.seed())
        return StochasticMeasurement(super().psi(), self.__H, self.__s, random=ran)

    def next(self, t, dt):
        # hamiltonian step
        super().set_p(runge_kutta(self.val_h_at, super().p(), t, dt))
        # stochastic step
        self.__last_r = self.gen_r()
        super().set_p(self.val_at(super().p(), self.__last_r))

    def last_r(self):
        return self.__last_r

    def gen_r(self):
        pp = self.prob_z_plus()
        a = self.rand.random_sample()
        if a < pp:
            return self.rand.normal(1, self.__s)
        return self.rand.normal(-1, self.__s)

    def prob_z_plus(self):
        return (1 + super().z()) / 2

    def val_at(self, p, r):
        a = -r / (self.__s ** 2)
        c = cosh(a)
        s = sinh(a)
        m = spinor(c - s, 0, 0, c + s)
        b = m * p * m.h()
        return b / b.trace()

    def val_h_at(self, p, t):
        return commutator(self.__H.eval(t), p) * -1j

