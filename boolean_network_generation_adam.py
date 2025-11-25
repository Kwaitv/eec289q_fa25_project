import util
import numpy as np


class AND:
    def __init__(self, inputs = None, output = None):
        self.inputs = inputs
        self.output = output

class OR:
    def __init__(self, inputs = None, output = None, val = None):
        self.inputs = inputs
        self.output = output
        self.val = val


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
        aset_dict: Dict {coeff: [(p1, p2), ...]}
        base_input_gate: The logic gate providing the base signal (e.g., '1')
    """
    
    # Registry to store constructed gates. 
    # Maps Coefficient (int) -> Gate Object
    term_registry = {
        1: 'input_wire'  # Base case: Coeff 1 is the input signal itself
    }

    # Helper to get a wire (either existing gate or raw value)
    def get_wire(val):
        if val in term_registry:
            return term_registry[val]
        else:
            # If term doesn't exist, we assume it's a raw 0 
            # or implies an error in the sort order of Aset_dict
            #print(f"Warning: Term {val} not found. Using 0.")
            return 0

    # Iterate through coefficients (ensure we build small terms before large ones)
    coeffs_queue = list(aset_dict_bin.keys())

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

        # CASE 1: Single Pair or Input Gate -> Create a simple SUM block
        if len(pairs) == 1 or input_gate:
                
            val_p1, val_p2 = aset_dict_val[coeff][input_pair_index]
            p1, p2 = aset_dict_bin[coeff][input_pair_index]

            # Create the Adder
            new_adder = Adder(f"Add_({val_p1, val_p2})")
            
            # Wire inputs (checking if they already exist)
            new_adder.set_pins(get_wire(util.compltoint(p1)), get_wire(util.compltoint(p2)))
            
            # Register this new adder as the source for 'coeff'
            term_registry[coeff] = new_adder
            print(f"Created Adder for {coeff} using inputs {val_p1} and {val_p2}")

        # CASE 2: Multiple Pairs -> Create MUX of SUMs
        else:
            print('In multiple pair/MUX case')
            all_inputs_constructed = True

            # Iterate through all possible constructions (tuples)
            for i, (p1, p2) in enumerate(pairs):
                lookup_result_p1 = get_wire(util.compltoint(p1))
                lookup_result_p2 = get_wire(util.compltoint(p2))

                if (lookup_result_p1 == 0 or lookup_result_p2 == 0):
                    all_inputs_constructed = False
                    break
            
            if (not all_inputs_constructed):
                coeffs_queue.append(coeff)
                continue
            
            print('All partial terms constructed')

            # Create the Mux
            new_mux = Mux(f"Mux_{coeff}")
            
            #print(f"Processing Mux for {coeff} with {len(pairs)} options:")
            
            # Iterate through all possible constructions (tuples)
            for i, (p1, p2) in enumerate(pairs):
                # Create an Adder for this specific option
                val_p1, val_p2 = aset_dict_val[coeff][i]

                option_adder = Adder(f"Add_{coeff}_opt({val_p1},{val_p2})")

                print(f"Created option Adder for {coeff}: {val_p1} and {val_p2}")
                
                # Wire the adder
                option_adder.set_pins(get_wire(util.compltoint(p1)), get_wire(util.compltoint(p2)))
                
                # Add this adder as an input to the Mux
                new_mux.add_input(option_adder)
                #print(f"  - Option {i}: Adder({p1}, {p2}) wired to Mux")

            # Register the Mux as the source for 'coeff'
            term_registry[coeff] = new_mux

            print(f"Created new Mux for {coeff}")


            if (len(coeffs_queue) == 0):
                last_mux = new_mux

    return last_mux

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

last_mux = build_adder_mux_network(Aset_dict_bin, Aset_dict_val)

#print_adder_mux_network(last_mux)
