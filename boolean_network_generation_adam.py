import util
import numpy as np


class LogicGate:
    """The abstract base class for all logic gates."""
    def __init__(self, label):
        self.label = label
        self.output = None

    def get_label(self):
        return self.label

    def get_output(self):
        """This method is implemented by the specific gate subclasses."""
        raise NotImplementedError()


class BinaryGate(LogicGate):
    """A class representing gates with two inputs (A and B)."""
    def __init__(self, label):
        super().__init__(label)
        self.pin_a = None
        self.pin_b = None
    
class Adder(BinaryGate):
    """Simulates an Arithmetic Adder (SUM block)."""
    def set_pins(self, gate1, gate2):
        self.pin_a = gate1
        self.pin_b = gate2
    
    def get_output(self):
        val_a = self.get_pin_value(self.pin_a)
        val_b = self.get_pin_value(self.pin_b)
        return val_a + val_b
    
class Mux(LogicGate):
    """
    Simulates a Multiplexer. 
    For this synthesis context, it takes a list of possible inputs.
    (In a real circuit, it would need a selector signal, here we default to index 0 
    or just store the candidates for synthesis analysis).
    """
    def __init__(self, label, inputs=None):
        super().__init__(label)
        self.inputs = inputs if inputs else []
        self.selector = 0 # Default to first input for simulation
        
    def add_input(self, gate):
        self.inputs.append(gate)
        
    def set_selector(self, index):
        self.selector = index

    def get_output(self):
        if not self.inputs:
            return 0
        # specific logic to retrieve the value of the selected input gate
        selected_gate = self.inputs[self.selector]
        if isinstance(selected_gate, LogicGate):
            return selected_gate.get_output()
        else:
            return int(selected_gate)

def build_adder_mux_network(aset_dict_bin, aset_dict_val):
    """
    Constructs the network based on the Aset_dict definitions.
    
    Args:
        aset_dict_bin: Dict {coeff: [(p1, p2), ...]} where p1, p2, ... are in 2's complement binary
        aset_dict_val: Dict {coeff: [(p1, p2), ...]} where p1, p2, ... are in decimal
    """
    
    # Registry to store constructed gates.
    # Maps Coefficient at level x to gate objects 
    # level (int) -> {coeff (int) -> Gate Object}
    term_registry = {
        0:{
            1: 'input_wire'  # Base case: Coeff 1 is the input signal itself
        }
    }

    # Helper to get a wire (either existing gate or raw value) and returns the last
    # logic level
    def get_wire(val):

        for logic_level in term_registry.keys():
            if val in term_registry[logic_level]:
                return term_registry[logic_level][val], logic_level
        
        # If term doesn't exist, we assume it's a raw 0 
        # or implies an error in the sort order of Aset_dict
        return 0, -1

    def connect_mux_inputs(mux, coeff, pairs, new_level=False):
        # Iterate through all possible constructions (tuples)
        for i, (p1, p2) in enumerate(pairs):
            # Create an Adder for this specific option
            val_p1, val_p2 = aset_dict_val[coeff][i]

            wire_p1 = -1
            wire_p2 = -1
            logic_level_p1 = -1
            logic_level_p2 = -1

            if (util.compltoint(p1) == 1):
                wire_p1 = f'1_<<_{np.log2(val_p1)}'
            else:
                wire_p1, logic_level_p1 = get_wire(util.compltoint(p1))

            if (util.compltoint(p2) == 1):
                wire_p2 = f'1_<<_{np.log2(val_p2)}'
            else:
                wire_p2, logic_level_p2 = get_wire(util.compltoint(p2))
            
            if (not new_level):
                last_logic_level = len(term_registry.keys())
                if (logic_level_p1 == last_logic_level or logic_level_p2 == last_logic_level):
                    continue

            option_adder = Adder(f"Add_{coeff}_opt({val_p1},{val_p2})")
            print(f"Created option Adder for {coeff}: {val_p1} and {val_p2}")

            option_adder.set_pins(wire_p1, wire_p2)
            
            # Add this adder as an input to the Mux
            mux.add_input(option_adder)

            return mux


    # Iterate through coefficients (ensure we build small terms before large ones)
    coeffs_queue = list(aset_dict_bin.keys())
    coeffs_queue.sort()

    last_mux = Mux('Empty Mux')

    input_pair_index = -1

    while len(coeffs_queue) > 0:

        print(f'Current coeff queue {coeffs_queue}')
        coeff = coeffs_queue.pop(0)
        pairs = aset_dict_bin[coeff]
        input_gate = False

        for i, (p1,p2) in enumerate(pairs):
            input_gate = util.compltoint(p1) == 1 and util.compltoint(p2) == 1
            input_pair_index = i

            if (input_gate):
                print('Found input gate')
                break

        # CASE 1: Input Gate -> Create a simple SUM block
        if input_gate:
                
            val_p1, val_p2 = aset_dict_val[coeff][input_pair_index]
            p1, p2 = aset_dict_bin[coeff][input_pair_index]

            # Create the Adder
            new_adder = Adder(f"Add_({val_p1, val_p2})")
            
            # Wire inputs         
            
            if (val_p1 == 1):
                wire_p1 = term_registry[0][1]
            else:
                wire_p1 = f'1_<<_{np.log2(val_p1)}'

            if (val_p2 == 1):
                wire_p2 = term_registry[0][1]
            else:
                wire_p2 = f'1_<<_{np.log2(val_p2)}'
                        
            new_adder.set_pins(wire_p1, wire_p2)
            
            # Register this new adder as the source for 'coeff'
            new_logic_level =  1

            if (new_logic_level not in term_registry):
                term_registry[new_logic_level] = {}

            term_registry[new_logic_level][coeff] = new_adder
            print(f"Created Adder for {coeff} using inputs {val_p1} and {val_p2}")

        # CASE 2: Multiple Pairs -> Create MUX of SUMs
        else:
            print('In multiple pair/MUX case')
            all_inputs_constructed = True

            # Iterate through all possible constructions (tuples)
            for i, (p1, p2) in enumerate(pairs):

                val_p1, val_p2 = aset_dict_val[coeff][i]

                wire_p1 = -1
                wire_p2 = -1
                logic_level_p1 = -1
                logic_level_p2 = -1

                if (util.compltoint(p1) == 1):
                    wire_p1 = f'1_<<_{np.log2(val_p1)}'
                else:
                    wire_p1, logic_level_p1 = get_wire(util.compltoint(p1))

                if (util.compltoint(p2) == 1):
                    wire_p2 = f'1_<<_{np.log2(val_p2)}'
                else:
                    wire_p2, logic_level_p2 = get_wire(util.compltoint(p2))
                
                if (wire_p1 == 0 or wire_p2 == 0):
                    all_inputs_constructed = False
            
            if (not all_inputs_constructed):
                coeffs_queue.append(coeff)
                print('Not all partial terms constructed')
                continue
            
            print('All partial terms constructed')

            # Create the Mux
            new_mux = Mux(f"Mux_{coeff}")
            
            connected_mux = connect_mux_inputs(new_mux, coeff, pairs)
            
            # Register the Mux as the source for 'coeff'            
            last_logic_level = len(term_registry.keys())

            if (len(connected_mux.inputs) > 0):            
                term_registry[last_logic_level][coeff] = connected_mux
            else:
                connected_mux = connect_mux_inputs(new_mux, coeff, pairs, new_level=True)
                new_logic_level = last_logic_level + 1

                term_registry[new_logic_level] = {}
                term_registry[new_logic_level][coeff] = connected_mux

            print(f"Created new Mux for {coeff}")

            if (len(coeffs_queue) == 0):
                last_mux = connected_mux

    return last_mux, term_registry

def print_adder_mux_network(logic_gate):
    """
    Recursively prints the structure of a LogicGate.
    """

    if logic_gate == 'input_wire':
        print('input_wire')
        return
    
    print(logic_gate.get_label())

    if isinstance(logic_gate, Adder):
        print_adder_mux_network(logic_gate.pin_a)
        print_adder_mux_network(logic_gate.pin_b)
    
    if isinstance(logic_gate, Mux):
        for gate in logic_gate.inputs:
            print_adder_mux_network(gate)
    

class AND:
    def __init__(self, p1 = None, p2 = None, pt = None):
        self.p1 = p1
        self.p2 = p2
        self.pt = pt

    def __repr__(self):
        return f'AND({self.pt},{self.p1},{self.p2})'

class OR:
    def __init__(self, ands = [], pt = None):
        self.ands = ands
        self.pt = pt

    def __repr__(self):
        or_str = f'OR({pt},['

        for and_gate in ands:
            or_str += and_gate
        
        or_str += '])'
        return or_str


def build_boolean_netowrk(Aset_dict_bin, Aset_dict_val, POs):
    ORs = {} # {pt:OR(pt,['p1_p2', 'p3_p4',...]), pt_next:OR(pt_next, 'p8_p9', ... ), ....}
    ANDs = {} # {'p1_p2':AND(p1,p2,pt), 'p3_p4':AND(p3,p4,pt), ...}
    Minimal_PTs = {} # {'opt3', 'opt5', 'opt9', ...}

    for po in POs:
        dfs(po)

    def dfs(pt):
        ORs[pt] = OR(pt)

        for i, (val_p1,val_p2) in Aset_dict_val[pt]:
            ANDs[f'{val_p1}_{val_p2}'] = AND(pt,val_p1,val_p2)
            ORs[pt].ands.append(f'{val_p1}_{val_p2}')

        if not minimal(p1):
            dfs(p1)
        else:
            Minimal_PTs.add(f'optvar{p1}')
    
        if not minimal(p2):
            dfs(p2)
        else:
            Minimal_PTs.add(f'optvar{p2}')

    def minimal(pt):
        minimal_val = False
        
        for i, (val_p1, val_p2) in Aset_dict_val[pt]:
            if util.compltoint(pt) == 1 and util.compltoint(pt) == 1:
                minimal_val = True
        
        return minimal_val


#coeffs = ['00011010', '01001011', '11111110', '11111111', '00000111', '01000001', '00001001', '00000100', '00011100', '10010110']
coeffs = ['00001111']
bit_width = len(coeffs[0])

Cset = [util.compltoint(util.odd(util.pos(coeff))) for coeff in coeffs]

# Use this for a more efficient queue structure
#Cset = deque(Cset)

#print('coeffs_pos_odd', Cset)

Cset.sort(reverse=True)

Aset_dict_bin = {}
Aset_dict_val = {}

while len(Cset) > 0:
#    print(f'Cset {Cset}')
    coeff = Cset.pop(0)

    if (coeff == 1):
        break

#    print(f'Constructing partial term pairs for {coeff}')
    
    partial_term_pairs_set_val, partial_term_pairs_set_bin = util.construct_partial_terms(util.inttocompl(coeff, bit_width))
#    print('partial term pairs in bin', partial_term_pairs_bin)

    # Flatten set of tuples into a set of distinct values
    partial_terms_set = {util.compltoint(item) for t in partial_term_pairs_set_bin for item in t}
    
    Cset = list(set(Cset + list(partial_terms_set)))
    Cset.sort(reverse=True)

    Aset_dict_bin[coeff] = partial_term_pairs_set_bin
    Aset_dict_val[coeff] = partial_term_pairs_set_val
#    print(f'Aset_dict_val[{coeff}] = {Aset_dict_val[coeff]}')
#    print(f'Aset_dict_bin[{coeff}] = {Aset_dict_bin[coeff]}')

#last_mux, term_registry = build_adder_mux_network(Aset_dict_bin, Aset_dict_val)

#print_adder_mux_network(last_mux)

build_boolean_netowrk(Aset_dict_bin, Aset_dict_val, coeffs)