

class Loop:

    def __init__(self, framerate, time_dependent_func=None, time_independent_func=None):
        self.__t = time_dependent_func is not None
        self.__e = time_independent_func is not None
        if self.__t:
            self.__dt = time_dependent_func
        if self.__e:
            self.__te = time_independent_func

        self.__del = 1.0 / framerate
        self.__last = 0
        self.__next = 0
        self.__dela = 0

    def name(self):
        if self.__t:
            return 'physics'
        return 'graphics'

    def init(self, time):
        self.__last = time
        self.__next = time + self.__del

    def go(self, dt):
        self.__dela += dt
        if self.__last + self.__dela >= self.__next:
            mul = int(self.__dela / self.__del)
            de = self.__del * mul

            if self.__t:
                self.__dt(de)
            if self.__e:
                self.__te()
            self.__last += de
            self.__next = self.__last + self.__del
            self.__dela -= de

    def act(self, dt, numtimes=-1):
        if numtimes == -1:
            self.__dela += dt
            numtimes = int(self.__dela / self.__del)
            self.__dela -= numtimes * self.__del
        self.actnow(dt, numtimes)

    def actnow(self, dt, numtimes=1):
        while numtimes > 0:
            if self.__t:
                self.__dt(self.__del)
            if self.__e:
                self.__te()
            numtimes -= 1

