import math as m
from graphics import Circle, screen_coords, lines, length_on_screen, line_info
from extramath import quaternion, spinor, ListFunction

sx = spinor(spinor(0, 1), spinor(1, 0))
sy = spinor(spinor(0, 1j), spinor(-1j, 0))
sz = spinor(spinor(1, 0), spinor(0, -1))
identity = spinor(spinor(1, 0), spinor(0, 1))

sigma_minus = spinor(0, 0, 1, 0)
sigma_plus = spinor(0, 1, 0, 0)


def rotate_matrix(theta, rotation_axis):
    return identity * m.cos(theta / 2) - (sx * rotation_axis[0] + sy * rotation_axis[1] + sz * rotation_axis[2])\
                                            * 1j * m.sin(theta / 2)


class Qubit:

    __strictness = .2
    __max_length = 200

    __num_records = 800

    __x_color = (220, 11, 10, 255)
    __y_color = (23, 240, 21, 255)
    __z_color = (11, 82, 239, 255)
    __mag_color = (20, 10, 80, 255)
    __noise_color = (170, 30, 50, 255)

    def __init__(self):
        self.__psi = None
        self.__ticks = 0

        self.__trackers = {}
        self.__graphics = False
        # self.__traj = []
        # self.__r = []
        # self.__track = False

    def add_tracker(self, name, evaluater, measure_initially=False):
        # creates a tracker list, first arg being what gives the
        # value and the second being the list of values from run
        self.__trackers[name] = [evaluater, [], measure_initially]

    def __copy__(self):
        from copy import deepcopy
        q = Qubit()
        q.__psi = self.__psi.__copy__()
        q.__ticks = self.__ticks

        q.__trackers = deepcopy(self.__trackers)
        q.__graphics = self.__graphics

        if q.__graphics:
            q.__pos = self.__pos.__copy__()
            q.__radius = self.__radius
            q.__lines = self.__lines[:]

            q.__list_x = deepcopy(self.__list_x)
            q.__list_y = deepcopy(self.__list_y)
            q.__list_z = deepcopy(self.__list_z)
            q.__list_mag = deepcopy(self.__list_mag)
            q.__list_noise = deepcopy(self.__list_noise)
            q.__graphs = self.__graphs

            q.__secs_per_loc = self.__secs_per_loc
            q.__tracker = self.__tracker

            q.__circles = self.__circles[:]

            q.__strictness = self.__strictness
            q.__max_length = self.__max_length
        return q

    def init_graphics(self, pos, radius):
        self.__graphics = True
        self.__pos = quaternion(0, *pos)
        self.__radius = radius
        self.__create_circles()
        self.__lines = []

        self.__list_x = None
        self.__list_y = None
        self.__list_z = None
        self.__list_mag = None
        self.__list_noise = None
        self.__graphs = False

        self.__secs_per_loc = 1
        self.__tracker = 0

    def set_graphics_rules(self, strictness=.06, max_length=200):
        self.__strictness = strictness
        self.__max_length = max_length

    # frames per loc is
    def add_state_graph(self, graph, secs_per_loc, x_col=__x_color, y_col=__y_color, z_col=__z_color,
                        mag_col=__mag_color, noise_col=__noise_color):
        self.__secs_per_loc = secs_per_loc
        self.__list_x = ListFunction(self.__num_records, (0, 1))
        self.__list_y = ListFunction(self.__num_records, (0, 1))
        self.__list_z = ListFunction(self.__num_records, (0, 1))
        self.__list_mag = ListFunction(self.__num_records, (0, 1))
        graph.add([self.__list_x, x_col],
                  [self.__list_y, y_col],
                  [self.__list_z, z_col],
                  [self.__list_mag, mag_col])
        graph.add_label([1500, 100], "x = red", x_col)
        graph.add_label([1500, 130], "y = green", y_col)
        graph.add_label([1500, 160], "z = blue", z_col)
        graph.add_label([1500, 190], "mag = navy", mag_col)

        if hasattr(self.__psi, 'last_r'):
            self.__list_noise = ListFunction(self.__num_records, (0, 1))
            graph.add([self.__list_noise, noise_col])
            graph.add_label([1500, 220], "noise = dark red", self.__noise_color)
        self.__graphs = True

    def __create_circles(self):
        self.__circles = []
        self.__circles.append(Circle(self.__pos, [self.__radius, 0, 0], .3))
        self.__circles.append(Circle(self.__pos, [0, self.__radius, 0], .3))
        self.__circles.append(Circle(self.__pos, [0, 0, self.__radius], .3))

    def init_psi(self, psi):
        self.__psi = psi
        self.__init_dt()

        for n in self.__trackers.items():
            n[1][1].clear()

    def measure(self):
        for n in self.__trackers.items():
            if n[1][2]:
                n[1][1].append(n[1][0](self.__psi))

    def __init_dt(self):
        self.__psi.create_density()

    def psi(self):
        return self.__psi.psi()

    def clear_traj(self):
        self.__trackers.clear()

    def get_traj(self, name):
        return self.__trackers[name][1]

    def x(self):
        return self.__psi.x()

    def y(self):
        return self.__psi.y()

    def z(self):
        return self.__psi.z()

    # def get_r(self):
    #     return self.__r

    def step(self, dt):
        self.__psi.next(self.__ticks * dt, dt)
        self.__init_dt()
        self.__ticks += 1

        # if self.__track:
        #     self.__traj.append(self.__psi.vec())
        #     if isinstance(self.__psi, StochasticMeasurement):
        #         self.__r.append(self.__psi.last_r())

        for n in self.__trackers.items():
            n[1][1].append(n[1][0](self.__psi))

        # self.__tracker = (self.__tracker + 1) % self.__frames_per_loc

        if self.__graphics:
            self.__trace(self.psi_vector())

            self.__tracker += dt / self.__secs_per_loc
            times = int(self.__tracker / self.__secs_per_loc)
            self.__tracker -= times * self.__secs_per_loc

            while times > 0:
                self.__draw_graphs()
                times -= 1

    def psi_vector(self):
        return quaternion(0, self.__psi.x(), self.__psi.y(), self.__psi.z()) * self.__radius

    def abs_square(self):
        return abs(self.__psi)

    @staticmethod
    def mix(color1, color2):
        return tuple([(color1[0] + color2[0]) / 2, (color1[1] + color2[1]) / 2,
                      (color1[2] + color2[2]) / 2, (color1[3] + color2[3]) / 2])

    @staticmethod
    def component(vec1, vec2, percent_vec1):
        return [vec1[0] * percent_vec1 + vec2[0] * (1 - percent_vec1),
                vec1[1] * percent_vec1 + vec2[1] * (1 - percent_vec1)]

    def draw(self, camera, circle_color, circle_grad_color, arrow_color, line_color, line_grad_color=()):
        self.__draw_lines(camera, line_color, line_grad_color)
        self.__circles[0].draw(camera, circle_color, color_gradient=circle_grad_color)
        self.__circles[1].draw(camera, circle_color, color_gradient=circle_grad_color)
        self.__circles[2].draw(camera, Qubit.mix(circle_color, circle_grad_color))
        if self.__psi is not None:
            Qubit.__add_dynamic_line(camera.transform(self.__pos), camera.transform(self.psi_vector()), arrow_color)

    def __draw_graphs(self):
        if self.__graphs:
            self.__list_x.add(self.__psi.x())
            self.__list_y.add(self.__psi.y())
            self.__list_z.add(self.__psi.z())
            self.__list_mag.add(abs(self.__psi))
            if self.__list_noise is not None:
                self.__list_noise.add(self.__psi.last_r() / 60)


    @staticmethod
    def __mag(complex_num):
        if isinstance(complex_num, complex):
            return (complex_num.real ** 2 + complex_num.imag ** 2) ** .5
        return complex_num

    def __trace(self, psi_vector):
        if len(self.__lines) == 0:
            self.__add_trace()
            return
        m = psi_vector - quaternion(*self.__lines[-1])
        if m.norm() >= self.__strictness:
            self.__add_trace()

    def __add_trace(self):
        self.__lines.append(self.psi_vector().to_vector())
        if self.__max_length == -1:
            return
        if len(self.__lines) > self.__max_length:
            self.__lines = self.__lines[1:]

    @staticmethod
    def __add_dynamic_line(quat1, quat2, color):
            vec_1 = screen_coords(quat1)
            vec_2 = screen_coords(quat2)
            segments = int(.4 * length_on_screen((quat1[1] + quat2[1]) / 2,
                                                 ((quat1[2] - quat2[2]) ** 2 +
                                                 (quat1[3] - quat2[3]) ** 2) ** .5)) + 1
            for x in range(1, segments + 1):
                lines.append(line_info(color, Qubit.component(vec_1, vec_2, x / segments),
                                       Qubit.component(vec_1, vec_2, (x - 1) / segments), 2,
                                       quat1.norm() * (x / segments) + quat2.norm() * (1 - x / segments)))

    @staticmethod
    def combine(color1, color2, percentage_1):
        return (color1[0] * percentage_1 + color2[0] * (1 - percentage_1),
                color1[1] * percentage_1 + color2[1] * (1 - percentage_1),
                color1[2] * percentage_1 + color2[2] * (1 - percentage_1),
                color1[3] * percentage_1 + color2[3] * (1 - percentage_1))

    def __draw_lines(self, camera, line_color, line_grad_color=()):
        transformed_vectors = []
        list_of_coords = []
        for line in self.__lines:
            transformed_vectors.append(camera.transform(line))
            list_of_coords.append(screen_coords(transformed_vectors[-1]))
        for x in range(1, len(list_of_coords)):
            if line_grad_color == () or self.__max_length == -1:
                color = line_color
            else:
                color = Qubit.combine(line_grad_color, line_color, (len(list_of_coords) - x) / self.__max_length)
            lines.append(line_info(color, list_of_coords[x - 1], list_of_coords[x], 2,
                                   (transformed_vectors[x].norm() + transformed_vectors[x - 1].norm()) / 2))
