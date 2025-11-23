def compltoint(bin_string):
    unsigned = int(bin_string, 2)
    if bin_string[0] == '1':
        return unsigned - (1 << len(bin_string))
    else:
        return unsigned


def inttocompl(n, width):
    mask = (1 << width) - 1
    return f'{n & mask:0{width}b}'


def complprint(bin_string):
    print(f"'{bin_string}' ({len(bin_string)
                             }-bit) converts to: {compltoint(bin_string)}")

def compl2val(bin_string, num_frac_bits = -1):

    print(f'bin_string {bin_string} with length {len(bin_string)}')
    if (num_frac_bits == -1):
        num_frac_bits = len(bin_string)

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

if __name__ == '__main__':
    for i in ['111111000101110100111010', '111011100011110001001010', '111111110111100000100000',
             '000000011110010100000011', '000001110111100111111000', '000001111100001010010010',
             '000000100000001000001100', '111110001000110111011101', '111100011010011110100010',
             '111100111111010100011111', '000000101011010111011000', '000110101110111000110101',
             '001101000010101010000111', '010001000011011001101010', '010001000011011001101010',
             '001101000010101010000111', '000110101110111000110101', '000000101011010111011000',
             '111100111111010100011111', '111100011010011110100010', '111110001000110111011101',
             '000000100000001000001100', '000001111100001010010010', '000001110111100111111000',
             '000000011110010100000011', '111111110111100000100000', '111011100011110001001010',
             '111111000101110100111010']:
        #print(eval('0b'+i))
        print(i, pos(i))

    print()
    for i in ['100000000000000000001111']:
        print(i, pos(i))

    print()
    for i in ['100000000000000000000111', '100000000000000000001011']:
        print(i, pos(i))


    for i in ['1111']:
        print(i, pos(i))
