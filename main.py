import gurobipy as gp
import scipy as sci
from enum import Enum, auto
from dataclasses import dataclass
from fixedpoint import FixedPoint
import util
import struct
# https://ieeexplore.ieee.org/document/4526735


# basic constructor should have just time
# represent coefficients as strings

class Filter_OPT:
    def __init__(self, timeout=2*60*60):
        self.timeout = timeout
        self.coeff = []
        self.fixpt = {}
        self.transform = {}
        self.stopband = 0
        self.passband = 0
        self.taps = 0
        self.width = 0
        self.qformat = {}
        self.qiformat = {}

        # bit vector 0(heuristic) 0(delay) 0(area)
        self.type = 0
        self.model = gp.Model('mcm', env=gp.Env())

        self.model.setParam('OutputFlag', 0)
        self.model.setParam('PoolSolutions', 1)
        self.model.setParam('PoolSearchMode', 2)
        self.model.setParam('TimeLimit', self.timeout)
        self.model.update()

    def file_load(self, path, passband, stopband):
        str_coeffs = []
        with open(path, 'r') as f:
            content = f.read()
            str_coeffs = (content
                          .replace('[', '')
                          .replace(']', '')
                          .replace(' ', '')
                          .replace('\n', '')
                          .split(','))

        self.qformat = util.genformat(len(str_coeffs[0]))
        self.qiformat = util.geniformat(len(str_coeffs[0]))

        for i in str_coeffs:
            x = FixedPoint(f'0b{i}', **self.qformat)
            self.coeff.append(x)
            self.fixpt[i] = FixedPoint(f'0b{i}', **self.qiformat)
            self.transform[i] = x

        self.passband = passband
        self.stopband = stopband
        self.taps = len(self.coeff)
        self.width = len(self.coeff[0])

    def print_coeff(self):
        for i in self.coeff:
            util.fp_print(i)

    # TODO
    def generate(self, passband, stopband, taps, width, ftype):
        self.passband = passband
        self.stopband = stopband
        self.taps = taps
        self.width = width

    # TODO
    def coeff_transform(self, type='BIN'):
        match type:
            case 'MSD':
                pass
            case 'CSD':
                pass
            case 'BIN':
                pass
            case _:
                pass
        pass

    # TODO
    def add_area(self):
        self.type += 1

        for i in self.transform:
            util.fp_print(self.transform[i])

        pass

    # TODO
    def add_delay(self):
        self.type += 2
        pass

    # TODO
    def add_heuristic(self):
        self.type += 4
        pass

    # TODO
    def show_sol(self):
        pass

    def optimize(self):
        if self.type > 0:
            self.model.optimize()
        else:
            self.add_area()
            self.model.optimize()


def main():
    fir1 = Filter_OPT()
    fir1.file_load(
        './filter-benchmarks/test-filters-table-0/coeffs/filter3-coeff.txt',
        0.25, 0.3)
    fir1.print_coeff()
    fir1.add_area()

    if 0 == 1:
        fir2 = Filter_OPT()
        fir2.file_load(
            './filter-benchmarks/test-filters-table-0/coeffs/filter5-coeff.txt',
            0.25, 0.3)
        fir2.add_area()
        fir2.add_delay()
        fir2.optimize()
        fir2.print_coeff()



if __name__ == "__main__":
    main()
