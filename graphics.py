import math as m
from extramath import quaternion
from pygame import font
from bisect import insort_left

PI = m.pi

windowSize = (1600, 600)

qubitLoc = (0, 0)
qubitSize = (800, 600)

graphLoc = (800, 0)
graphSize = (800, 600)

view_angle = 40 * PI / 180
depth = qubitSize[0] / (2 * m.tan(view_angle / 2))


RED = (0xff, 0x00, 0x00, 0xff)
GREEN = (0x00, 0xff, 0x00, 0xff)
BLUE = (0x00, 0x00, 0xff, 0xff)
CYAN = (0x00, 0xaa, 0xaa, 0xff)
WHITE = (0xff, 0xff, 0xff, 0xff)
BLACK = (0x00, 0x00, 0x00, 0xff)

FOREST_GREEN = (0x35, 0xf5, 0x0b, 0xff)
SKY_BLUE = (0x6e, 0xa1, 0xf5, 0xff)

PURPLE = (0x9a, 0x1d, 0xf6, 0xff)


def x_coord(x, y):
    if x == 0:
        if y == 0:
            return qubitLoc[0] + qubitSize[0] / 2
        return -1
    return qubitLoc[0] + qubitSize[0] / 2 - depth * y / x


def y_coord(x, z):
    if x == 0:
        if z == 0:
            return qubitLoc[1] + qubitSize[1] / 2
        return -1
    return qubitLoc[1] + qubitSize[1] / 2 + depth * z / x


def length_on_screen(distance, length):
    return depth * abs(length / distance)


def screen_coords(quat):
    return [int(x_coord(quat[1], quat[2])), int(y_coord(quat[1], quat[3]))]


def color_mult(color, scale):
    return tuple([color[0] * scale, color[1] * scale, color[2] * scale, color[3] * scale])


class Circle:

    __pos = None

    # a vector orthogonal to the plane of the Circle, magnitude is radius of Circle
    __r = None
    __thickness = 0.0

    def __init__(self, pos, r, thickness=0.0):
        if isinstance(pos, quaternion):
            self.__pos = pos
        else:
            self.__pos = quaternion(0, *(pos[:3]))
        if isinstance(r, quaternion):
            self.__r = r
        else:
            self.__r = quaternion(0, *(r[:3]))
        self.__thickness = thickness

    def radius(self):
        return self.__r.norm()

    def move(self, vec4):
        self.__pos += vec4

    def rotate(self, r_matrix):
        self.__r = (r_matrix * self.__r.T).T

    @staticmethod
    def __quat(quat_1, quat_2, p, t):
        return quat_1 * m.cos(t * 2 * PI) + quat_2 * m.sin(t * 2 * PI) + p

    @staticmethod
    def add(color1, color2):
        return [x + y for x, y in zip(color1, color2)]

    def draw(self, camera, color, color_gradient=None):
        pos = camera.transform(self.__pos)
        r = camera.rotate(self.__r)
        vec_1 = r.cross(camera.rotate([-1 / 2 ** .5, 1 / 2 ** .5, 0]))
        vec_1 = vec_1.normalized() * self.radius()
        vec_2 = r.cross(vec_1).normalized() * self.radius()

        precision = int(.7 * length_on_screen(pos.norm(), self.radius()))
        for t in range(0, precision):
            v1 = self.__quat(vec_1, vec_2, pos, (t - 1) / precision)
            v2 = self.__quat(vec_1, vec_2, pos, t / precision)
            one = screen_coords(v1)
            two = screen_coords(v2)
            width = max(int(length_on_screen(v1.norm(), self.__thickness)), 1)
            if color_gradient is not None:
                dif = abs((2 * t / precision - 1))
                lines.append(line_info(Circle.add(color_mult(color, dif), color_mult(color_gradient, 1 - dif)),
                                       one, two, width, v2.norm()))
            else:
                lines.append(line_info(color, one, two, width, v2.norm()))


class line_info:

    def __init__(self, color, p1, p2, width, distance):
        self.__c = color
        self.__p1 = p1
        self.__p2 = p2
        self.__wid = width
        self.__z = distance

    def c(self):
        return self.__c

    def p1(self):
        return self.__p1

    def p2(self):
        return self.__p2

    def width(self):
        return self.__wid

    def __le__(self, other):
        return self.__z >= other.__z

    def __ge__(self, other):
        return self.__z <= other.__z

    def __lt__(self, other):
        return self.__z > other.__z

    def __gt__(self, other):
        return self.__z < other.__z

    def __eq__(self, other):
        return self.__z == other.__z


class Lines:

    def __init__(self):
    # contains [color, vector 1, vector 2, width, distance (from camera)]
        self.__lines = []

    def append(self, line_info):
        # self.__lines.append(line_info)
        insort_left(self.__lines, line_info)

    def draw(self, drawer, screen):
        # self.__lines = sorted(self.__lines, key=lambda a: -float(a[4]))
        for x in self.__lines:
            drawer.line(screen, x.c(), x.p1(), x.p2(), x.width())
        self.__lines = []
        # screen.set_at((100, 100), (100, 100, 100))


class Words:

    def __init__(self):
        # words contain [location, text, color]
        self.__words = []
        font.init()
        self.__font = font.SysFont("sans-serif", 30)

    def append(self, loc, text, color):
        self.__words.append([loc, text, color])

    def draw(self, screen):
        for word in self.__words:
            surface = self.__font.render(word[1], True, word[2])
            screen.blit(surface, word[0])
        self.__words = []



lines = Lines()
words = Words()


def draw(drawer, screen):
    lines.draw(drawer, screen)
    words.draw(screen)
