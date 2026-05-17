from sim2 import *

def series():
    ec = Circuit(0.01, 5)
    n1 = Node("N1")
    n2 = Node("N2")
    gnd = Node("GND", gnd=True)

    u = VoltageSource(gnd, n1, 5, "U", I0=1)
    r1 = Resistor(n1, n2, 100, "R1", I0=2)
    r2 = Resistor(n2, gnd, 200, "R2", I0=3)

    ec.add_nodes([n1, n2, gnd])
    ec.add_components([u, r1, r2])

    print(ec.solve()[-1])

series()