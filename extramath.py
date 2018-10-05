import math as m


class spinor:

    __name__ = 'spinor'

    def __init__(self, alpha, beta, alpha2=None, beta2=None):
        if alpha2 is not None and beta2 is not None:
            # forms like this:
            # [ alpha    beta  ]
            # [ alpha2   beta2 ]
            self.__a = spinor(alpha, alpha2)
            self.__b = spinor(beta, beta2)
        else:
            self.__a = alpha
            self.__b = beta

    def __repr__(self):
        if self.is_matrix():
            return '((' + str(self[0][0]) + ', ' + str(self[1][0]) + '), (' +\
                   str(self[0][1]) + ', ' + str(self[1][1]) + '))'
        return '(' + str(self.__a) + ', ' + str(self.__b) + ')'

    def __add__(self, other):
        return spinor(self.__a + other.__a, self.__b + other.__b)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return spinor(-self.__a, -self.__b)

    def __mul__(self, other):
        if isinstance(other, spinor):
            if other.is_matrix():
                one = self.t()
                return spinor(spinor(one[0] * other[0], one[1] * other[0]),
                              spinor(one[0] * other[1], one[1] * other[1]))
            if self.is_matrix():
                return spinor(self[0] * other, self[1] * other)
            return self.__a * other.__a + self.__b * other.__b
        return spinor(self.__a * other, self.__b * other)

    def __truediv__(self, other):
        return spinor(self.__a / other, self.__b / other)

    def __setitem__(self, key, value):
        if key == 0:
            self.__a = value
        elif key == 1:
            self.__b = value
        else:
            raise IndexError('index out of range of spinor: ' + str(key))

    def __getitem__(self, item):
        if item == 0:
            return self.__a
        elif item == 1:
            return self.__b
        else:
            raise IndexError('index out of range of spinor: ' + str(item))

    def __abs__(self):
        return complex(self.__a * complex(self.__a).conjugate() + self.__b * complex(self.__b).conjugate()).real

    def norm(self):
        return abs(self) ** .5

    def normalized(self):
        return self / self.norm()

    def conjugate(self):
        return spinor(self[0].conjugate(), self[1].conjugate())

    def is_matrix(self):
        return isinstance(self[0], spinor) and isinstance(self[1], spinor)

    def t(self):
        if self.is_matrix():
            return spinor(spinor(self[0][0], self[1][0]), spinor(self[0][1], self[1][1]))
        else:
            raise TypeError('not a matrix')

    def h(self):
        # conjugate transpose
        if self.is_matrix():
            return self.t().conjugate()
        else:
            raise TypeError('not a matrix')

    def trace(self):
        if self.is_matrix():
            return self[0][0] + self[1][1]
        else:
            raise TypeError('not a matrix')

    def __copy__(self):
        return spinor(self.__a, self.__b)


class quaternion:

    suf = ['', 'i', 'j', 'k']

    __name__ = 'quaternion'

    # in the form a + bi + cj + dk
    def __init__(self, *args):
        if len(args) == 4:
            self.__a = list(args)
        elif len(args) == 3:
            self.__a = [0] + list(args)
        else:
            raise ValueError('Illegal number of arguments: ' + str(len(args)))

    def __repr__(self):
        ret = ''
        for x in range(4):
            if self.__a[x] == 0:
                continue
            if len(ret) == 0:
                ret += str(self.__a[x]) + quaternion.suf[x]
            elif self.__a[x] > 0:
                ret += ' + ' + str(self.__a[x]) + quaternion.suf[x]
            else:
                ret += ' - ' + str(abs(self.__a[x])) + quaternion.suf[x]
        if ret == '':
            return '0'
        return ret

    def __add__(self, other):
        return quaternion(*(a + b for a, b in quaternion.combine(self, other)))

    def __sub__(self, other):
        return quaternion(*(a - b for a, b in quaternion.combine(self, other)))

    def __neg__(self):
        return quaternion(*(-a for a in self))

    def __mul__(self, other):
        if not isinstance(other, quaternion):
            if isinstance(other, int) or isinstance(other, float):
                return quaternion(*(other * x for x in self.__a))
            else:
                raise ValueError('cannot divide quaternion by ' + other.__name__)
        else:
            return quaternion(self[0] * other[0] - self[1] * other[1] - self[2] * other[2] - self[3] * other[3],
                              self[1] * other[0] + self[0] * other[1] - self[3] * other[2] + self[2] * other[3],
                              self[2] * other[0] + self[3] * other[1] + self[0] * other[2] - self[1] * other[3],
                              self[3] * other[0] - self[2] * other[1] + self[1] * other[2] + self[0] * other[3])

    def dot(self, other):
        return sum(a * b for a, b in quaternion.__vector_part_2(self, other))

    def cross(self, other):
        return quaternion(0, *(a for a in quaternion.__cross_combo(self, other)))

    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return quaternion(*(x / other for x in self.__a))
        else:
            raise ValueError('cannot divide quaternion by ' + other.__name__)

    def __setitem__(self, key, value):
        self.__a[key] = value

    def __getitem__(self, item):
        return self.__a[item]

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        self.n += 1
        if self.n <= len(self.__a):
            return self[self.n - 1]
        raise StopIteration

    def __copy__(self):
        return quaternion(*self)

    def c(self):
        return quaternion(*quaternion.__conjugate(self))

    def norm(self):
        return abs(self) ** .5

    def unit(self):
        return self / self.norm()

    def __abs__(self):
        return sum(x * x for x in self.__a)

    def __pow__(self, power, modulo=None):
        if isinstance(power, int):
            if power == 0:
                return quaternion(1, 0, 0, 0)
            if power < 0:
                return self.__reciprocal() ** (-power)
            return self * self ** (power - 1)
        else:
            raise ValueError('cannot raise quaternion to non-integer power')

    def __reciprocal(self):
        return self.c() / abs(self)

    def normalized(self):
        return quaternion(*self.__a) / self.norm()

    def to_vector(self):
        return self[1:]

    # rotation vector about axis (x, y, z) theta degrees (right-handed)
    @staticmethod
    def euler_form(theta, x, y, z):
        sin = m.sin(theta / 2)
        return quaternion(m.cos(theta / 2), sin * x, sin * y, sin * z).normalized()

    @staticmethod
    def rotate_quaternion(vector, theta, x, y, z):
        q = quaternion.euler_form(theta, x, y, z)
        return q * quaternion(0, *vector), q ** -1

    @staticmethod
    def combine(q1, q2):
        for x in range(4):
            yield (q1[x], q2[x])

    @staticmethod
    def __conjugate(q):
        for x in range(4):
            if x == 0:
                yield (q[x])
            else:
                yield (-q[x])

    @staticmethod
    def __vector_part_2(q1, q2):
        for x in range(1, 4):
            yield (q1[x], q2[x])

    @staticmethod
    def __cross_part_2(q1, q2):
        for x in range(1, 4):
            yield (q1[x % 3 + 1] * q2[(x + 1) % 3 + 1])

    @staticmethod
    def __cross_combo(q1, q2):
        for x, y in zip(quaternion.__cross_part_2(q1, q2), quaternion.__cross_part_2(q2, q1)):
            yield (x - y)


one = quaternion(1, 0, 0, 0)


class const_hamiltonian:

    def __init__(self, val):
        self.__val = val


class Function:

    def __init__(self, funct, domain=None):
        self.__function = funct
        if domain is None:
            self.__domain = lambda *x: True
        else:
            self.__domain = domain

    def __call__(self, *args, **kwargs):
        if self.in_domain(*args):
            return self.__function(*args)
        return False

    def domain(self):
        return self.__domain

    def in_domain(self, *args):
        if isinstance(self.__domain, tuple or list):
            return self.__domain[0] <= args[0] <= self.__domain[1]
        return self.__domain(*args)

    def below_domain(self, arg):
        if isinstance(self.__domain, tuple):
            return arg < self.__domain[0]
        return False

    def above_domain(self, arg):
        if isinstance(self.__domain, tuple):
            return arg > self.__domain[1]
        return False


class Piecewise:

    def __init__(self, *functions):
        self.__functions = sorted(functions, key=lambda a: a.domain()[0])

    def __call__(self, *args, **kwargs):
        return self.__call_help(0, len(self.__functions), *args)

    def __call_help(self, mine, maxe, *args):
        pos = int((mine + maxe) / 2)
        if self.__functions[pos].in_domain(*args):
            return self.__functions[pos](*args)
        if pos > mine:
            if self.__functions[pos].below_domain(args[0]):
                return self.__call_help(mine, pos, *args)
        if pos < maxe - 1:
            if self.__functions[pos].above_domain(args[0]):
                return self.__call_help(pos + 1, maxe, *args)
        return False


class ListFunction(Function):

    def __init__(self, num, dom):
        super().__init__(lambda x: self.__get(x), dom)
        self.__num = num
        self.__list = []
        self.__loc = 0

    def add(self, item):
        if len(self.__list) == self.__num:
            self.__list[self.__loc] = item
            self.__loc = (self.__loc + 1) % self.__num
        else:
            self.__list.append(item)

    def __get_pos(self, x):
        return (x - super().domain()[0]) * self.__num / (super().domain()[1] - super().domain()[0])

    def __get(self, x):
        xx = self.__get_pos(x)
        x = int(xx)
        perc = xx - x
        if 0 <= xx <= len(self.__list) - 1:
            if x < len(self.__list) - 1:
                return (1 - perc) * self.__list[(self.__loc + x) % self.__num]\
                       + perc * self.__list[(self.__loc + x + 1) % self.__num]
            return self.__list[(self.__loc + x) % self.__num]
        return False

