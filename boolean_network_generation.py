import util
import numpy as np

class AND:
    def __init__(self, p1, p2, pt):
        self.p1 = p1
        self.p2 = p2
        self.pt = pt
        self.en = 0

    def __repr__(self):
        return f'AND({self.pt},{self.p1},{self.p2})'


class OR:
    def __init__(self, pt=None):
        self.ands = []
        self.pt = pt

    def __repr__(self):

        return f"OR({self.pt},[{', '.join(self.ands)}])"','


def build_boolean_network(Aset_dict_bin, Aset_dict_val, POs):

    ORs = {} # {pt:OR(pt,['p1_p2', 'p3_p4',...]), pt_next:OR(pt_next, 'p8_p9', ... ), ....}
    ANDs = {} # {'p1_p2':AND(p1,p2,pt), 'p3_p4':AND(p3,p4,pt), ...}
    Minimal_PTs = set([]) # ['opt3', 'opt5', 'opt9', ...]


    def minimal(pt):
        minimal_test = False

        temp_pt = util.iodd(pt)

        if temp_pt == 1:
            return True

        for i, (p1, p2) in enumerate(Aset_dict_bin[pt]):
            if util.compltoint(p1) == 1 and util.compltoint(p2) == 1:
                minimal_test = True
        return minimal_test

    def bfs(PTs):
        #print(f'Calling BFS with {PTs}')

        if (len(PTs) == 0):
            return

        next_PTs = set([])

        bool_tran = util.nop
        if 1:
            bool_tran = util.iodd

        for pt in PTs:

            if minimal(pt):
                Minimal_PTs.add(pt)
                continue

            ORs[pt] = OR(pt=pt)

            for i, (val_p1, val_p2) in enumerate(Aset_dict_val[pt]):
                if (val_p1 in PTs or val_p2 in PTs):
                    continue
                int_p1, int_p2 = map(bool_tran, [val_p1, val_p2])
                sorted_p1, sorted_p2 = util.order(int_p1, int_p2)

                ANDs[f'{sorted_p1}_{sorted_p2}_{pt}'] = \
                    AND(sorted_p1, sorted_p2, pt)

                ORs[pt].ands.append(f'{sorted_p1}_{sorted_p2}_{pt}')

                # Extract positive and odd coefficients
                for pt_int in map(util.compltoint, Aset_dict_bin[pt][i]):
                    if minimal(pt_int):
                        Minimal_PTs.add(pt_int)
                    else:
                        #print(f'Adding PT {pt_int}')
                        next_PTs.add(pt_int)

        bfs(next_PTs)

        return

    bfs(POs)
    return ORs, ANDs, Minimal_PTs

def build_aset_dict(coeffs):
    bit_width = len(coeffs[0])
    Cset = [util.compltoint(util.odd(util.pos(coeff))) for coeff in coeffs \
                if util.compltoint(coeff) != 0 and util.compltoint(coeff) != -1]

    # Use this for a more efficient queue structure
    # Cset = deque(Cset)

    # print('coeffs_pos_odd', Cset)

    Cset.sort(reverse=True)

    Aset_dict_bin = {}
    Aset_dict_val = {}

    while len(Cset) > 0:
        coeff = Cset.pop(0)

        if (coeff == 1):
            break

        partial_term_pairs_set_val, partial_term_pairs_set_bin = util.construct_partial_terms(util.inttocompl(coeff, bit_width))
        # Flatten set of tuples into a set of distinct values
        partial_terms_set = {util.compltoint(item) for t in partial_term_pairs_set_bin for item in t}

        Cset = list(set(Cset + list(partial_terms_set)))
        Cset.sort(reverse=True)

        Aset_dict_bin[coeff] = partial_term_pairs_set_bin
        Aset_dict_val[coeff] = partial_term_pairs_set_val

    return Aset_dict_bin, Aset_dict_val


if __name__ == '__main__':

    coeffs = ['00001111']

    coeffs_int = [util.compltoint(coeff) for coeff in coeffs]

    Aset_dict_bin, Aset_dict_val = build_aset_dict(coeffs)

    ORs, ANDs, Minimal_PTs = build_boolean_network(Aset_dict_bin, Aset_dict_val, coeffs_int)

    Minimal_PTs_arr = sorted(list(Minimal_PTs))

    print(ORs)
    print(ANDs)
    print(Minimal_PTs)
