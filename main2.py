from sim2 import *

def series():
    ec = Circuit(0.01, 500)
    n1 = Node("N1")
    n2 = Node("N2")
    gnd = Node("GND", gnd=True)

    u = VoltageSource(gnd, n1, "U", 5)
    r1 = Resistor(n1, n2, "R1", 100)
    r2 = Resistor(n2, gnd, "R2", 200)

    ec.add_nodes([n1, n2, gnd])
    ec.add_components([u, r1, r2])

    print(ec.solve())

series()