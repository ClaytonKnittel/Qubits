import math as m
from extramath import quaternion

r_speed = m.pi / 32
a_speed = m.pi / 32
m_speed = 2

mouse_sensitivity = .02


class EventLog(object):

    def __init__(self):
        self.__events = []
        self.__click_pos = ()
        self.__is_clicked = False
        self.__just_clicked = False
        self.__mul = 1

    def log(self, event_id):
        self.__events.append(event_id)

    def remove(self, event_id):
        self.__events.remove(event_id)

    def click(self):
        self.__is_clicked = True
        self.__just_clicked = True

    def unclick(self):
        self.__is_clicked = False

    def d_pos(self, pos):
        if self.__click_pos is not ():
            return tuple([pos[0] - self.__click_pos[0], pos[1] - self.__click_pos[1]])
        return tuple([0, 0])

    def act(self, mouse_pos):
        for x in self.__events:
            if x == 97:                     # a
                camera.r_rotate(r_speed)
            elif x == 115:                  # s
                camera.a_rotate(a_speed)
            elif x == 100:                  # d
                camera.r_rotate(-r_speed)
            elif x == 119:                  # w
                camera.a_rotate(-a_speed)
            elif x == 109:
                camera.move(m_speed)
            elif x == 107:
                camera.move(-m_speed)

            if x == 276:
                self.__mul = .2
            elif x == 275:
                self.__mul = 4
            else:
                self.__mul = 1

        if self.__is_clicked and not self.__just_clicked:
            dpos = self.d_pos(mouse_pos)
            camera.r_rotate(-dpos[0] * mouse_sensitivity)
            camera.a_rotate(dpos[1] * mouse_sensitivity)
        elif self.__just_clicked:
            self.__just_clicked = False
        self.__click_pos = mouse_pos

    def time_mul(self):
        return self.__mul

    def print(self):
        print(self.__events)


class Camera:

    __d = 0
    __radial = 0
    __azimuthal = 0
    __transform = None
    __transform_inverse = None
    __translate = None

    def __init__(self, d, radial, azimuthal):
        self.__d = d
        self.__radial = radial
        self.__azimuthal = azimuthal
        self.__set_transform_matrix()

    def transform(self, quat):
        return self.translate(self.rotate(quat))

    def transform_inverse(self, quat):
        return self.rotate_inverse(self.translate_inverse(quat))

    def rotate(self, quat):
        if isinstance(quat, quaternion):
            return self.__transform * quat * self.__transform_inverse
        return self.__transform * quaternion(0, *quat) * self.__transform_inverse

    def rotate_inverse(self, quat):
        if isinstance(quat, quaternion):
            return self.__transform_inverse * quat * self.__transform
        return self.__transform_inverse * quaternion(0, *quat) * self.__transform

    def translate(self, quat):
        return quat + self.__translate

    def translate_inverse(self, quat):
        return quat - self.__translate

    def r_rotate(self, angle):
        self.__radial += angle
        self.__set_transform_matrix()

    def a_rotate(self, angle):
        self.__azimuthal += angle
        self.__set_transform_matrix()

    def move(self, move):
        self.__d += move
        self.__set_transform_matrix()

    def __set_transform_matrix(self):
        self.__transform = self.a_matrix(self.__azimuthal) * self.r_matrix(self.__radial)
        self.__transform_inverse = self.__transform.c()
        self.__translate = quaternion(0, -self.__d, 0, 0)

    @staticmethod
    def a_matrix(angle):
        return quaternion.euler_form(angle, 0, 1, 0)

    @staticmethod
    def r_matrix(angle):
        return quaternion.euler_form(-angle, 0, 0, 1)


camera = Camera(60, .4, .4)
event_log = EventLog()
