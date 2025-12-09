import random
from ilp_mapping import ilp_mapping
from boolean_network_generation import build_aset_dict, build_boolean_network
from boolean_network_generation import AND, OR
from util import inttocompl, compltoint, pos, odd
from pathlib import Path

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

def parse_directory(directory_path):
    coeffs = []
    folder = Path(directory_path)

    if not folder.is_dir():
        raise NotADirectoryError(f"'{directory_path}' is not a valid directory.")
    
    for file_path in sorted(folder.glob('*.txt')):
        try:
            with open(file_path, 'r') as f:
                # Parse the individual file
                row_data = f.read()
                row_data = row_data.replace('[','').replace(']\n','')
                coeffs_row = row_data.split(', ')
                
                # Check consistency: Ensure we only add valid lists
                if isinstance(coeffs_row, list):
                    coeffs.append(coeffs_row)
                else:
                    print(f"Skipping {file_path.name}: Content is not a list.")
                    
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

    return coeffs

def count_ones(bit_str):
   return bit_str.count('1') 

def coeff_size_heur(bit_str):
    return 2**(count_ones(bit_str) - 1) - 1

if __name__ == '__main__':
    coeff_sets = parse_directory('filter-benchmarks/remez-filters-table-2/coeffs')

    for i,coeff_set in enumerate(coeff_sets):
        print('Working on coeff_set', i)

        filter_bin_set_i = set(coeff_set) # remove duplicates
        filter_pos_odd = [odd(pos(coeff)) for coeff in filter_bin_set_i \
                             if compltoint(coeff) != 0 and compltoint(coeff) != -1]

        filter_bin_set_f = list(set(filter_pos_odd)) # remove duplicates
        print(len(filter_bin_set_f))
        print("walk values", sum([coeff_size_heur(val) for val in filter_bin_set_f]))

        print('Finished normalizing coeffs')
        Aset_dict_bin, Aset_dict_val = build_aset_dict(filter_bin_set_f)

        filter_vals = [compltoint(coeff) for coeff in filter_bin_set_f if compltoint(coeff) != 1]
        filter_sorted = filter_vals.sort(reverse=True)

        print('Generating boolean network')
        ORs, ANDs, Minimal_PTs = build_boolean_network(Aset_dict_bin, Aset_dict_val, filter_vals)

        Minimal_PTs_arr = sorted(list(Minimal_PTs))

        print('Entering ILP mapping and calling Gurobi')
        ilp_mapping(filter_vals, Minimal_PTs, Minimal_PTs_arr, ANDs, ORs)
