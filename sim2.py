import numpy as np
import matplotlib.pyplot as plt


class Circuit:
    def __init__(self, delta_t, N_t):
        self.delta_t = delta_t
        self.N_t = N_t

        self.nodes = []
        self.comps = []
        # self.next_id = 0
        # self.id_quantity = []
        # self.id_subscripts = []
        # self.probe_id = []
    
    def add_nodes(self, nodes):
        self.nodes.extend(nodes)
    
    def add_components(self, comps):
        self.comps.extend(comps)
    
    def total_eq_count(self):
        count = 0
        for node in self.nodes:
            if node.has_kcl_eq:
                count += 1
        for comp in self.comps:
            count += type(comp).eq_count
        return count

    def solve(self):
        state0 = np.array(Con.initial_values)
        dim = np.size(state0)

        A = np.zeros((dim, dim))
        b = np.zeros(dim)
        states = np.empty((self.N_t, dim))
        states[0] = state0

        n = 0
        for node in self.nodes:
            if node.has_kcl_eq and not node.gnd:
                node.row_kcl_eq(A[n])
                b[n] = 0
                n += 1
            if node.gnd:
                A[n, node.id] = 1
                b[n] = 0
                n += 1
        for n_t in range(self.N_t - 1):
            for comp in self.comps:
                comp.modify_b(b, states[n_t])
            states[n_t + 1] = np.linalg.solve(A, b)
        

class Node:
    def __init__(self, name=None, gnd=False, U0=0, probe=False):
        self.name = name
        self.gnd = gnd
        self.id = Con.new_id(self.name, U0, probe)
        self.probe = probe
        
        self.cons = []

        self.has_kcl_eq = True
        if self.gnd:
            self.has_kcl_eq = False
        
    
    def connect(self, con, out):
        con.out = out
        self.cons.append(con)

    def row_kcl_eq(self, An):
        # 0 = sum(Iin) - sum(Iout)

        for con in self.cons:
            An[con.id] = -1 if con.out else 1

class Con:
    ids = []
    initial_values = []
    probes = []

    def new_id(name, initial_value, probe, pin_name=None):
        if name is None:
            comp_name = f"{Component.symbol}{len(Con.ids)}"
        comp_name = f"{name}{len(Con.ids)}"

        if pin_name is not None:
            comp_name += f"({pin_name})"
        name = f"$I_{{{comp_name}}}$"
        
        Con.ids.append(name)
        Con.initial_values.append(initial_value)
        Con.probes.append(probe)
        return len(Con.ids) - 1

    def __init__(self, node, id):
        self.node = node
        self.id = id
        self.out = None

    def I0(self, value=None):
        if value is not None:
            Con.initial_values[self.id] = value
        return Con.initial_values[self.id]
        

class Component:
    symbol = "K"
    has_kcl = True
    eq_count = 1
    def __init__(self, ins: list[Con], outs: list[Con], name: str=None):
        self.ins = ins
        for i in self.ins:
            i.node.connect(i, False)
        
        self.outs = outs
        for o in self.outs:
            o.node.connect(o, True)
        
        self.name = name
    
    def row_comp_eq(self, A, b, n, delta_t):
        pass
    
    def row_internal_kcl_eq(self, A, n):
        An = A[n]
        for i in self.ins:
            An[i.id] = 1
        for o in self.ins:
            An[o.id] = -1
    
    def modify_b(self, b, n, state):
        pass


class Component2(Component):
    has_kcl = False
    eq_count = 1
    def __init__(self, n_in, n_out, name=None, I0=0, probe=False):
        id = Con.new_id(name, I0, probe)
        ins  = [Con(n_in, id)]
        outs = [Con(n_out, id)]
        super().__init__(ins, outs, name)

class Resistor(Component2):
    def __init__(self, n_in, n_out, R, name=None, I0=0, probe=False):
        super().__init__(n_in, n_out, name, I0, probe)
        self.R = R

class VoltageSource(Component2):
    def __init__(self, n_in, n_out, U, name=None, I0=0, probe=False):
        super().__init__(n_in, n_out, name, I0, probe)
        self.U = U

# class OpAmp(Component):
#     # n_ins[0] = n_plus
#     # n_ins[1] = n_minus
#     def __init__(self, n_plus, n_minus, n_out, name, amplification=10**7, I0=None, probe=False):
#         super().__init__([n_plus, n_minus], [n_out], name, I0, probe)
#         self.amplification = amplification
    
#     # Uout = amplification * ((U+) - (U-))
#     # in A: Uout - amplification * (U+) + amplification * (U-)
#     # in b: 0

#     def row_comp_eq(self, A, b, n, delta_t):
#         self.row_index = n

#         An = A[self.row_index]
#         An[self.n_out.voltage_id] = 1
#         An[self.n_ins[0].voltage_id] = -self.amplification
#         An[self.n_ins[1].voltage_id] = self.amplification

#         b[self.row_index] = 0

#         return n + 1