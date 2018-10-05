

def mathematica_str(array):
    array = array.replace('[', '{')
    array = array.replace(']', '}')
    array = array.replace('\'', '')
    array += ';'
    return array


def individual(qubit, end_condition, dt=1 / 128.0):
    q = qubit.__copy__()
    q.measure()
    if isinstance(end_condition, int):
        while end_condition > 0:
            q.step(dt)
            end_condition -= 1
    elif type(end_condition) == type(lambda: 0) and end_condition.__name__ == (lambda: 0).__name__:
        while not end_condition():
            q.step(dt)
    else:
        raise Exception('end condition must either be a number or a lambda')
    return q

def group_avg(start_qubit, end_condition, num_avgs, dt=128.0):
    l = []
    while num_avgs > 0:
        l.append(start_qubit.__copy__())
    pass
