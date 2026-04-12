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
    ec = Circuit(0.1, 100)
    n1 = Node("N1")
    n2 = Node("N2", probe=True)
    gnd = Node("GND", gnd=True)

    u = VoltageSource(gnd, n1, "U", 5)
    r = Resistor(n1, n2, "R", 100, probe=True)
    c = Capacitor(n2, gnd, "C", 0.025)

    ec.add_nodes([n1, n2, gnd])
    ec.add_components([u, r, c])

    ec.solve()


def ulc():
    T = 200
    N_t = 2000
    ec = Circuit(T / N_t, N_t)
    n1 = Node("N1")
    n2 = Node("N2", probe=True)
    gnd = Node("GND", gnd=True)

    u = VoltageSource(gnd, n1, "U", 5)
    l = Inductor(n1, n2, "L", 100, probe=True)
    c = Capacitor(n2, gnd, "C", 0.025)

    ec.add_nodes([n1, n2, gnd])
    ec.add_components([u, l, c])

    ec.solve()

def lc():
    T = 200
    N_t = 200000
    ec = Circuit(T / N_t, N_t)

    n = Node("N", probe=True)
    gnd = Node("GND", gnd=True)

    l = Inductor(gnd, n, "L", 100, I0=0.1, probe=True)
    c = Capacitor(n, gnd, "C", 0.025)

    ec.add_nodes([n, gnd])
    ec.add_components([l, c])

    ec.solve()



lc()