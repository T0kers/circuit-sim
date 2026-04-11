from components import *


def series_with_singular():
    ec = Circuit()
    n1 = Node("N1")
    n2 = Node("N2")
    gnd = Node("GND", gnd=True)
    u1 = VoltageSource(gnd, n1, "U1", 5)
    r1 = Resistor(n1, n2, "R1", 100)
    r2 = Resistor(n2, gnd, "R2", 100)

    n3 = Node("N3")
    r3 = Resistor(n3, gnd, "R3", 100)

    ec.add_nodes([n1, n2, gnd, n3])
    ec.add_components([u1, r1, r2, r3])

    print(ec.solve())



def parallel():
    ec = Circuit(0.01, 500)
    n1 = Node("N1")
    gnd = Node("GND", gnd=True)
    u1 = VoltageSource(gnd, n1, "U1", 5)
    r1 = Resistor(n1, gnd, "R1", 100)
    r2 = Resistor(n1, gnd, "R2", 100)

    ec.add_nodes([n1, gnd])
    ec.add_components([u1, r1, r2])

    print(ec.solve())

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

def rc():
    ec = Circuit(0.01, 1000)
    n1 = Node("N1")
    n2 = Node("N2", probe=True)
    gnd = Node("GND", gnd=True)

    u = VoltageSource(gnd, n1, "U", 5)
    r = Resistor(n1, n2, "R1", 100, probe=True)
    c = Capacitor(n2, gnd, "R2", 0.05)

    ec.add_nodes([n1, n2, gnd])
    ec.add_components([u, r, c])

    print(ec.solve())


rc()