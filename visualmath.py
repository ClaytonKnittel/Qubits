from graphics import lines, graphLoc, graphSize, words, line_info


class Graph:

    __cushion = 10
    __axis_width = 2
    __graph_width = 2

    # function_color given as [function, color] list
    def __init__(self, dom, ran, *function_color):
        self.__functions = function_color
        self.__dom = dom
        self.__ran = ran
        self.__set_width()
        self.__set_height()
        self.__axis_color = (0, 0, 0, 255)
        self.__graph_color = (0, 255, 0, 255)
        self.__labels = []

    def set_draw_colors(self, axis_color, graph_color=(0, 255, 0, 255)):
        self.__axis_color = axis_color
        self.__graph_color = graph_color

    def add_label(self, loc, text, color):
        self.__labels.append([loc, text, color])

    def add(self, *function_color):
        self.__functions += function_color

    def __set_width(self):
        self.__width = graphSize[0] - 2 * self.__cushion

    def __set_height(self):
        self.__height = graphSize[1] - 2 * self.__cushion

    def __x_loc(self, x):
        return x + graphLoc[0] + self.__cushion

    def __y_loc(self, y):
        return graphLoc[1] + graphSize[1] - self.__cushion\
               - (y - self.__ran[0]) * self.__height / (self.__ran[1] - self.__ran[0])

    def __num_to_val(self, x):
        return (x / self.__width - self.__dom[0]) * (self.__dom[1] - self.__dom[0])

    def __draw_text(self):
        for label in self.__labels:
            words.append(label[0], label[1], label[2])

    def draw(self):
        lines.append(line_info(self.__axis_color,
                               (self.__x_loc(0), self.__y_loc((self.__ran[0] + self.__ran[1]) / 2)),
                               (self.__x_loc(self.__width), self.__y_loc((self.__ran[0] + self.__ran[1]) / 2)),
                               self.__axis_width, 1))
        lines.append(line_info(self.__axis_color, (self.__x_loc(0), self.__y_loc(self.__ran[0])),
                               (self.__x_loc(0), self.__y_loc(self.__ran[1])), self.__axis_width, -1))

        for f in self.__functions:
            if isinstance(f, list):
                fu = f[0]
                color = f[1]
            else:
                fu = f
                color = self.__graph_color
            prev = fu(0)
            for x in range(1, self.__width + 1):
                nex = fu(self.__num_to_val(x))
                if nex and prev is not False:
                    lines.append(line_info(color, (self.__x_loc(x - 1), self.__y_loc(prev)),
                                           (self.__x_loc(x), self.__y_loc(nex)), self.__graph_width, 0))
                prev = nex

        self.__draw_text()

