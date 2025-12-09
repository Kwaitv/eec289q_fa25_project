#import os
#os.environ['GRB_LICENSE_FILE'] = '/home/k6vu/.local/opt/gurobi/gurobi.lic'
import gurobipy as gp
import boolean_network_generation as bn

# data format

# input set of ANDs and open

# vars represnting minimal PTs
# vars representing outputs of ANDSs
# vars representing non minmal PTS (OR outputs)
# vars represnting minimal PT and 1<<n (minmal sum or smth)

# generate gurobipi model
# run sorted

def ilp_mapping(coeffs_int, Minimal_PTs, Minimal_PTs_arr, ANDs, ORs):
    #print(Minimal_PTs_arr)
    pts = Minimal_PTs_arr + sorted(list(ORs.keys()))
    #print('pts',pts)

    def has_shift(key):
        return key.split("_")[0] == "1"

    mcm_ilp = gp.Model('multiple constant multiplication', env=gp.Env())

    mcm_ilp.setParam('OutputFlag', 0)
    mcm_ilp.setParam('PoolSolutions', 1)
    mcm_ilp.setParam('PoolSearchMode', 2)
    # mcm_ilp.setParam('TimeLimit', 10*60*60)
    mcm_ilp.setParam('TimeLimit', 60)
    mcm_ilp.update()


    prime_pt = mcm_ilp.addVars(
        Minimal_PTs, name='primal', vtype=gp.GRB.BINARY)

    and_pt = mcm_ilp.addVars(
        ANDs, name='and', vtype=gp.GRB.BINARY)

    or_pt = mcm_ilp.addVars(
        ORs, name='or', vtype=gp.GRB.BINARY)

    shift_pt = mcm_ilp.addVars(
        filter(has_shift, ANDs.keys()), name='shift', vtype=gp.GRB.BINARY)

    # enumerating time
    #print("primal:", prime_pt, "\n")
    #print("and", and_pt, "\n")
    #print("or", or_pt, "\n")
    #print("shift", shift_pt, "\n")

    # And Constraints
    for and_gate in ANDs:
        pt1, pt2, pt = map(int, and_gate.split("_"))
        #print("and gate", pt1, pt2, pt, ANDs[and_gate])
        C = and_pt[and_gate]
        A = shift_pt[f'{pt1}_{pt2}_{pt}'] if (pt1 == 1) else \
            prime_pt[pt1] if (pt1 in Minimal_PTs_arr) else \
            or_pt[pt1]
        B = prime_pt[pt2] if (pt2 in Minimal_PTs_arr) else \
            or_pt[pt2] 
            
        mcm_ilp.addConstr(A - C >= 0)
        mcm_ilp.addConstr(B - C >= 0)
        mcm_ilp.addConstr(C - A - B >= -1)

    # instantiate ors after
    for or_gate in ORs:
        #print(or_gate, ORs[or_gate])
        C = or_pt[or_gate]
        reduce = 0
        count = 0

        for impl in ORs[or_gate].ands:
            A = and_pt[impl]
            mcm_ilp.addConstr(C - A >= 0)
            reduce += A
            count += 1

        mcm_ilp.addConstr(reduce - C >= 0)
        mcm_ilp.update()
        #print("reduce:", reduce - C)

    # set POs high
    for or_gate in or_pt:
        if or_gate in coeffs_int:
            #print("PO", or_gate)
            mcm_ilp.addConstr(or_pt[or_gate] == 1)

    mcm_ilp.setObjective(
        prime_pt.sum() + and_pt.sum(),
        gp.GRB.MINIMIZE)


    mcm_ilp.update()
    # pre run
    #print()
    #print("Model Pre Run")
    #print("primes", prime_pt)

    #print("AND Gates")
    #for and_gate in and_pt:
        #print(and_gate, and_pt[and_gate])

    #print("OR Gates")
    #for or_gate in or_pt:
        #print(or_gate, or_pt[or_gate])

    #print("shifts")
    #for shift in shift_pt:
        #print(shift, shift_pt[shift])


    mcm_ilp.update()
    mcm_ilp.optimize()
    mcm_ilp.update()

    # print solution
    #print()
    #print("Model Post Run")
    #print(prime_pt)

    #print("AND Gates")
    #for and_gate in and_pt:
        #print(and_gate, and_pt[and_gate])

    #print("OR Gates")
    #for or_gate in or_pt:
        #print(or_gate, or_pt[or_gate])

    #print("Shifted options")
    #for shift in shift_pt:
        #print(shift, shift_pt[shift])

    print('Final number of adders', mcm_ilp.ObjVal)
