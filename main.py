import gurobipy as gp
import scipy as sci
from enum import Enum, auto
from dataclasses import dataclass
# https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1688880


class Filter_OPT:
    def __init__(self, band, taps, width, timeout=2*60*60):
        self.timeout = timeout
        self.band = band
        self.taps = taps
        self.width = width
        self.models = [None, None, None]
        self.results = []
        self.coeff = sci.signal.remez(taps, band)

    @dataclass
    class Results:
        var_n: int
        clause_n: int
        optv: int
        adders: int
        steps: int
        runtime: float

    class Model(Enum):
        MAA = auto()
        MAMDA = auto()
        MAMDH = auto()

    def init_model(self, model):
        match model:
            case self.Model.MAA:
                self.init_maa()
            case self.Model.MAMDA:
                self.init_mamda()
            case self.Model.MAMDH:
                self.init_mamdh()
            case _:
                print("Model Specified Incorrectly")

    def init_maa(self):
        # Minimum Area Algorithm (MAA)
        # optimiznig heuristic
        self.models[self.Model.MAA.value] = gp.Model("MAA")

    def init_mamda(self):
        # Minimum Area and Minimum Delay Algorithm (MAMDA)
        # - search spac ereduction
        self.models[self.Model.MAA.value] = gp.Model("MAMDA")

    def init_mamdh(self):
        # Minimum Area and Minimum Delay Heuristic (MAMDH)
        # - search spac ereduction
        self.models[self.Model.MAA.value] = gp.Model("MAMDH")

    def opt(self, model):
        if self.models[model.value] is None:
            self.init_model(model)

        if self.models[model.value] is None:
            exit

        print(self.models[model.value].runtime)


# some network representation class


# Post processing for Minimum Delay (PPMD)
# -


# algorithm inputs
# - pass band, stop band
# - number of taps
# - width

# solver intermediates
# - solver variables, solver clauses, objective value

# output heuristics
# - number of adders
# - steps (need to dig into what that means)
# - solver runtime

def main():
    filter = Filter_OPT((0.10, 0.15), 100, 8)
    filter.opt(Filter_OPT.Model.MAA)


if __name__ == "__main__":
    main()
