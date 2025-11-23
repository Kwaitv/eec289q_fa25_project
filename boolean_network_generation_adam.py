import util 

#coeffs = ['00011010', '01001011', '11111110', '11111111', '00000111', '01000001', '00001001', '00000100', '00011100', '10010110']
coeffs = ['00001111']
bit_width = len(coeffs[0])

Cset = [util.compltoint(util.odd(util.pos(coeff))) for coeff in coeffs]

# Use this for a more efficient queue structure
#Cset = deque(Cset)

print('coeffs_pos_odd', Cset)

Cset.sort()

Aset_dict = {}

while len(Cset) > 0:
    coeff = Cset.pop(0)

    if (coeff == 1):
        break

    print(f'Constructing partial term pairs for {coeff}')
    
    partial_term_pairs_bin = util.construct_partial_terms(util.inttocompl(coeff, bit_width))
    print('partial term pairs in bin', partial_term_pairs_bin)

    partial_terms_set_bin = {item for t in partial_term_pairs_bin for item in t}
    
    partial_terms_set = {util.compltoint(term) for term in partial_terms_set_bin}
    
    Cset = Cset + list(partial_terms_set)
    Cset.sort(reverse=True)

    Aset_dict[coeff] = partial_terms_set
    print(f'Aset_dict[{coeff}] = {Aset_dict[coeff]}')

