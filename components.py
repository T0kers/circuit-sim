import numpy as np
import matplotlib.pyplot as plt

class CurrentId:
    # Standard direction means that the assumed current flow is positive when going from the in terminal to the out terminal
    def __init__(self, index, standard_direction):
        self.index = index
        self.standard_direction = standard_direction
    
    def get_sign(self):
        return 1 if self.standard_direction else -1

class Circuit:
    def __init__(self, delta_t, N_t):
        self.delta_t = delta_t
        self.N_t = N_t

        self.nodes = []
        self.components = []
        self.next_id = 0
        self.id_symbols = []
        self.id_subscripts = []
        self.probe_id = []

    def new_id(self, symbol, subscript="", probe=False):        
        self.next_id += 1
        self.id_symbols.append(symbol)
        self.id_subscripts.append([subscript])
        self.probe_id.append(probe)
        return self.next_id - 1
    
    def attach_to_id(self, index, standard_direction, subscript, probe):
        sign = "" if standard_direction else "-"
        self.id_subscripts[index].append(sign + subscript)
        self.probe_id[index] |= probe
        return CurrentId(index, standard_direction)

    # id is the index for the VOLTAGE variable
    def add_nodes(self, nodes):
        for node in nodes:
            self.nodes.append(node)
    
    # id is the index for the CURRENT variable
    def add_components(self, components):
        for component in components:
            self.components.append(component)
        
    def id_search(self):
        for index in range(len(self.nodes)):
            self.id_search_node(index)
            
    def id_search_node(self, node_index):
        node = self.nodes[node_index]
        if node.voltage_id is not None:
            return

        con_count = node.connection_count()
        match con_count:
            case 0:
                node.has_kcl_eq = False
                print(f'Node "{node.name}" has no connections.')
                return
            case 1:
                print(f'Node "{node.name}" has only one connection.')
            case 2:
                node.voltage_id = self.new_id("U", node.name, node.probe)
                node.has_kcl_eq = False

                current_index = None

                # True if assumed current direction is positive when going from components in-terminal to out terminal
                # meaing from the node POV, coming from an out node, and going to an in node
                is_standard_direction = True

                # First component determines the current direction
                is_first_comp = True

                for con, from_out in zip(node.connections, node.connections_is_out):
                    if con.current_id is not None:
                        current_index = con.current_id.index
                        is_first_comp = False
                        is_standard_direction = from_out == con.current_id.standard_direction
                
                if current_index is None:
                    current_index = self.new_id("I")
                
                for con, to_out in zip(node.connections, node.connections_is_out):
                    if con.current_id is not None:
                        if con.current_id.index == current_index:
                            continue
                        else:
                            print(node_index)
                            raise Exception("Unreachable, hopefully")
                    
                    # The component "recieves standard direction current" if the node has standard_direction and it is going to an in node (see previous comment)
                    con.current_id = self.attach_to_id(current_index, standard_direction=is_first_comp or is_standard_direction != to_out, subscript=con.name, probe=con.probe)

                    if to_out:
                        self.id_search_node(self.nodes.index(con.n_in))
                    else:
                        self.id_search_node(self.nodes.index(con.n_out))
                return

        # Runs for con_count == 1 and con_count > 2
        node.voltage_id = self.new_id("U", node.name)
        for con, to_out in zip(node.connections, node.connections_is_out):
            if con.current_id is None:
                con.current_id = CurrentId(self.new_id("I", con.name, con.probe), True)
                if to_out:
                    self.id_search_node(self.nodes.index(con.n_in))
                else:
                    self.id_search_node(self.nodes.index(con.n_out))
    
    def solve(self):
        self.id_search()
        dim = self.next_id
        A = np.zeros((dim, dim))
        b = np.zeros(dim)
        states = np.zeros((self.N_t, dim))

        n = 0
        for node in self.nodes:
            if node.has_kcl_eq and not node.gnd:
                A[n] = node.row_kcl_eq(dim)
                b[n] = 0
                n += 1
            if node.gnd:
                A[n, node.voltage_id] = 1
                b[n] = 0
                n += 1
        
        for component in self.components:
            component.row_comp_eq(A, b, n, self.delta_t)
            n += 1

        for n_t in range(self.N_t - 1):
            for component in self.components:
                component.modify_b(b, states[n_t])
            states[n_t + 1] = np.linalg.solve(A, b)
        
        t = np.linspace(0, self.N_t * self.delta_t, self.N_t, endpoint=False)
        figs = []
        for n in range(dim):
            if not self.probe_id[n]:
                continue
            fig, ax = plt.subplots()
            ax.plot(t, states[:, n])
            ax.set_title(f"{self.id_symbols[n]}({" ".join(self.id_subscripts[n])})")
            figs.append(fig)

        plt.show()

        return states

class Node:
    def __init__(self, name, gnd=False, probe=False):
        self.name = name
        self.gnd = gnd
        self.is_dependent = gnd
        self.probe = probe
        
        self.connections = []
        self.connections_is_out = []

        self.has_kcl_eq = True # This is false is node only have 0 or 2 in/outputs, because the kcl equation is then uneccesary
        self.voltage_id = None
    
    def in_connect(self, comp):
        # self.in_connections.append(comp)
        self.connections.append(comp)
        self.connections_is_out.append(False)
    
    def out_connect(self, comp):
        # self.out_connections.append(comp)
        self.connections.append(comp)
        self.connections_is_out.append(True)
    
    # Returns row for A-matrix
    def row_kcl_eq(self, row_dim):
        # 0 = sum(Iin) - sum(Iout)
        An = np.zeros(row_dim)

        for connection, from_out in zip(self.connections, self.connections_is_out):
            An[connection.current_id.index] = -1 if from_out else 1
        
        return An
    
    def connection_count(self):
        return len(self.connections)

# Current is positive when flowing from in -> out
class Component:
    def __init__(self, n_in, n_out, name, probe=False):
        self.n_in = n_in
        self.n_in.in_connect(self)

        self.n_out = n_out
        self.n_out.out_connect(self)

        self.name = name
        self.probe = probe

        # Current as in electricity not as in "now"
        self.current_id = None
    
    def row_comp_eq(self, A, b, row_index, delta_t):
        self.row_index = row_index
    
    def modify_b(self, b, state):
        pass
    

class Resistor(Component):
    def __init__(self, n_in, n_out, name, R, probe=False):
        super().__init__(n_in, n_out, name, probe)
        self.R = R

    # 0 = Uin - Uout - Rself * Iself
    # in A: Uin - Uout - Rself * Iself
    # in b: 0
    def row_comp_eq(self, A, b, row_index, delta_t):
        super().row_comp_eq(A, b, row_index, delta_t)

        An = A[self.row_index]
        An[self.n_in.voltage_id] = 1
        An[self.n_out.voltage_id] = -1
        An[self.current_id.index] = -self.current_id.get_sign() * self.R

        b[self.row_index] = 0


class Capacitor(Component):
    def __init__(self, n_in, n_out, name, C, probe=False):
        super().__init__(n_in, n_out, name, probe)
        self.C = C
    
    # I(t+dt) * dt = C * ((U(t+dt) - U(t))
    # where: U(t) = Uin(t) - Uout(t)
    # C * (Uin(t) - Uout(t)) = C * Uin(t+dt) - C * Uout(t+dt) - I(t+dt) * dt

    # in A: C * Uin(t+dt) - C * Uout(t+dt) - I(t+dt) * dt
    # in b: C * (Uin(t) - Uout(t))

    def row_comp_eq(self, A, b, row_index, delta_t):
        super().row_comp_eq(A, b, row_index, delta_t)

        An = A[self.row_index]
        An[self.n_in.voltage_id] = self.C
        An[self.n_out.voltage_id] = -self.C
        An[self.current_id.index] = -self.current_id.get_sign() * delta_t
    
    def modify_b(self, b, state):
        b[self.row_index] = self.C * (state[self.n_in.voltage_id] - state[self.n_out.voltage_id])
    

class VoltageSource(Component):
    def __init__(self, n_in, n_out, name, U, probe=False):
        super().__init__(n_in, n_out, name, probe)
        self.U = U
    
    # Uself = Uout - Uin
    # in A: Uout - Uin
    # in b: Uself

    def row_comp_eq(self, A, b, row_index, delta_t):
        super().row_comp_eq(A, b, row_index, delta_t)
        
        An = A[self.row_index]
        An[self.n_out.voltage_id] = 1
        An[self.n_in.voltage_id] = -1

        b[self.row_index] = self.U
        

class CurrentSource(Component):
    def __init__(self, n_in, n_out, name, probe=False):
        super().__init__(n_in, n_out, name, probe)