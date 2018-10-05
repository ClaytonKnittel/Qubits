from extramath import spinor
import evolutions as ev
import qubit as q
from numpy import pi, sqrt


test = True

sq2 = 1 / 2 ** .5

qubit = q.Qubit()

qubit.init_psi(ev.StochasticMeasurement(spinor(sq2, sq2), q.identity, 1))
# qubit.init_psi(ev.Schrodinger(spinor(1 / 2, 1j * sqrt(3 / 4 - 4 / 25) + 2 / 5), q.sx))
qubit.add_tracker('traj', lambda q: [q.x(), q.y(), q.z()])


def convert(lis):
    return (str(lis)).replace('[', '{').replace(']', '}').replace('e', ' 10^').replace(' ', '')


if test:
    from tester import individual
    dt = 1 / 2048.0
    steps = int(pi / dt)
    q = individual(qubit, steps, dt=dt)
    print(convert(q.get_traj('traj')))
else:
    qubit.init_graphics([0, 0, 0], 10)
    from visualizer import run
    run(qubit)
