import random
from ilp_mapping import ilp_mapping
from boolean_network_generation import build_aset_dict, build_boolean_network
from boolean_network_generation import AND, OR
from util import inttocompl, compltoint, pos, odd

def first_set_coeffs(seed = ''):
    
    if seed == '':
        curr_seed = random.randint(1,10**6)
    else:
        curr_seed = seed
        random.seed(curr_seed)
    
    print('Using seed', curr_seed)

    coeff_sets = []
    coeff_dict = {}
    for num in range(10,101):
        coeff_dict[num] = []
        for _ in range(30):
            coeff_set = []
            for _ in range(num):
                coeff = random.randint(-2**11,2**11-1)
                coeff_set.append(coeff)
        coeff_sets.append(coeff_set)
    
    return coeff_sets

def parse_file(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()

            # 1. Remove brackets
            content = content.replace('[','').replace(']\n','')
            # 2. Split by comma
            coeffs = content.split(', ')
            return coeffs
    except FileNotFoundError as e:
        print(f'Error finding file: {e}')
        return []

if __name__ == '__main__':
    #coeff_sets = first_set_coeffs()
    filter1_file_name = 'filter-benchmarks/remez-filters-table-2/coeffs/filter1-coeff.txt'
    
    filter1_bin = parse_file(filter1_file_name)
    filter1_bin_set_i = set(filter1_bin) # remove duplicates
    filter1_pos_odd = [odd(pos(coeff)) for coeff in filter1_bin_set_i \
                        if compltoint(coeff) != 0 and compltoint(coeff) != -1]
    filter1_bin_set_f = list(set(filter1_pos_odd)) # remove duplicates

    Aset_dict_bin, Aset_dict_val = build_aset_dict(filter1_bin_set_f)

    filter1 = [compltoint(coeff) for coeff in filter1_bin_set_f if compltoint(coeff) != 1]

    ORs, ANDs, Minimal_PTs = build_boolean_network(Aset_dict_bin, Aset_dict_val, filter1)

    Minimal_PTs_arr = sorted(list(Minimal_PTs))

    ilp_mapping(filter1, Minimal_PTs, Minimal_PTs_arr, ANDs, ORs)