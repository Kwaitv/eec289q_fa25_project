import math

def compltoint(bin_string):
    unsigned = int(bin_string, 2)
    if bin_string[0] == '1':
        return unsigned - (1 << len(bin_string))
    else:
        return unsigned

def inttocompl(n, width):
    mask = (1 << width) - 1
    return f'{n & mask:0{width}b}'

def odd(fp):
    while int(fp) % 2 != 1:
        fp = fp >> 1
    return fp

def complprint(bin_string):
    print(f"'{bin_string}' ({len(bin_string)
                             }-bit) converts to: {compltoint(bin_string)}")

def compl2val(bin_string, num_frac_bits = -1):

    print(f'bin_string {bin_string} with length {len(bin_string)}')
    if (num_frac_bits == -1):
        num_frac_bits = len(bin_string)

    print(f'Num fractional bits: {num_frac_bits}')
    
    val = 0
    positional_weights = [weight - num_frac_bits for weight in range(len(bin_string)-1, -1, -1)]
    print("positional_weights", positional_weights)

    for weight, bin_val in zip(positional_weights, bin_string):
        if (weight == positional_weights[0]):
            print(f'Subtracting {2**weight}*{int(bin_val)}={2**weight * int(bin_val)}')
            val -= 2**weight * int(bin_val)
        else:
            print(f'Adding {2**weight}*{int(bin_val)}={2**weight * int(bin_val)}')
            val += 2**weight * int(bin_val)
    return val

def pos(binary_string):
    new_string = list(binary_string)
    if binary_string[0] == '1':
        for idx, i in enumerate(binary_string):
            if i == '0':
                new_string[idx] = '1'
            else:
                new_string[idx] = '0'
        
        new_string = "".join(new_string)
        
        bit_width = len(new_string)
        val = compltoint(new_string)
        val += 1
        return inttocompl(val, bit_width)
    else:
        return "".join(new_string)

def odd(binary_string):

    while binary_string[-1] != '1':
        binary_string = binary_string[:-1]
        binary_string = '0' + binary_string
    
    return binary_string

# returns a list of tuples
def construct_partial_terms(partial_term_bin):
    bit_width = len(partial_term_bin)
    partial_term = compltoint(partial_term_bin)

    partial_term_pairs = [(term1, term2) for term1, term2 in zip(range(1, partial_term, 1), range(partial_term-1, 0, -1))]
    partial_term_pairs = partial_term_pairs[:math.ceil(len(partial_term_pairs)/2)]

    partial_term_pairs_pos_odd = [(odd(pos(inttocompl(term1, bit_width))), (odd(pos(inttocompl(term2, bit_width)))))
                                for (term1, term2) in partial_term_pairs]
    
    partial_term_pairs_set_bin = list({tuple(sorted(x)) for x in partial_term_pairs_pos_odd})
    partial_term_pairs_set_val = []

    for (bin_term1, bin_term2) in partial_term_pairs_set_bin:
        for (int_term1, int_term2) in partial_term_pairs:
            # if bin_term1 shifted to the left in (int_term1, int_term2)
            # and bin_term2 be shifted to the left in (int_term1, int_term2)
            # then, add to partial_term_paris_set_val

            reduced_term1 = compltoint(bin_term1)
            reduced_term2 = compltoint(bin_term2)

            found_match1 = reduced_term1 in (int_term1, int_term2)

            shift_val = 1

            while not found_match1 and shift_val < bit_width:
                shifted_reduced_term1 = reduced_term1 << shift_val
                
                found_match1 = shifted_reduced_term1 in (int_term1, int_term2)
                
                shift_val += 1

            found_match2 = reduced_term2 in (int_term1, int_term2)
            
            shift_val = 1

            while not found_match2 and shift_val < bit_width:
                shifted_reduced_term2 = reduced_term2 << shift_val
                
                found_match2 = shifted_reduced_term2 in (int_term1, int_term2)
                
                shift_val += 1
            
            if found_match1 and found_match2:
                partial_term_pairs_set_val.append((int_term1, int_term2))
                break

    new_partial_term_pairs_set_val = set([])
    new_partial_term_pairs_set_bin = set([])

    for i, (val_term1, val_term2) in enumerate(partial_term_pairs_set_val):
        
        val_term1_bin = inttocompl(val_term1, bit_width)
        val_term2_bin = inttocompl(val_term2, bit_width)

        reduced_term1_bin, reduced_term2_bin = partial_term_pairs_set_bin[i]

        include_term = True

        for i, bit in enumerate(val_term1_bin):
            if val_term1_bin[i] == '1' and val_term2_bin[i] == '1':
                include_term = False

        if include_term:
            new_partial_term_pairs_set_val.add((val_term1, val_term2))
            new_partial_term_pairs_set_bin.add((reduced_term1_bin, reduced_term2_bin))
    
    return list(new_partial_term_pairs_set_val), list(new_partial_term_pairs_set_bin)

#if __name__ == '__main__':
#    for i in ['111111000101110100111010', '111011100011110001001010', '111111110111100000100000',
#             '000000011110010100000011', '000001110111100111111000', '000001111100001010010010',
#             '000000100000001000001100', '111110001000110111011101', '111100011010011110100010',
#             '111100111111010100011111', '000000101011010111011000', '000110101110111000110101',
#             '001101000010101010000111', '010001000011011001101010', '010001000011011001101010',
#             '001101000010101010000111', '000110101110111000110101', '000000101011010111011000',
#             '111100111111010100011111', '111100011010011110100010', '111110001000110111011101',
#             '000000100000001000001100', '000001111100001010010010', '000001110111100111111000',
#             '000000011110010100000011', '111111110111100000100000', '111011100011110001001010',
#             '111111000101110100111010']:
#        x = FixedPoint(f'0b{i}', **qformat)
#        fp_print(x)


#    print()
#    for i in ['100000000000000000001111']:
#        x = FixedPoint(f'0b{i}', **qformat)
#        fp_print(x)

#    print()
#    for i in ['100000000000000000000111', '100000000000000000001011']:
#        x = FixedPoint(f'0b{i}', **qformat)
#        fp_print(x)

#    qformat = genformat(4)
#    for i in ['1111']:
#        x = FixedPoint(f'0b{i}', **qformat)
#        fp_print(x)
