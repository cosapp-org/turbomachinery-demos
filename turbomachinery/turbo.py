from cosapp.systems import System
from cosapp.ports import Port

import numpy as np

from mftmaps.compressor import SimplifiedMftCompressor
from thermo.ideal_gas import IdealGas


class FluidPort(Port):
    
    def setup(self):
        self.add_variable("W", 0.)
        self.add_variable("pt", 101325.)
        self.add_variable("Tt", 288.15)


class Compressor(System):

    def setup(self):

        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        self.add_inward('pcnr', 90.)
        self.add_inward('gh', 0.)
        self.add_inward('cmp_model', SimplifiedMftCompressor())
        self.add_inward('gas', IdealGas(288.15, 1004.))

    def compute(self):
        self.fl_out.Tt = self.gas.t_from_h(self.gas.h(self.fl_in.Tt) + self.cmp_model.ghr(self.gh))
        self.fl_out.pt = self.fl_in.pt * self.cmp_model.pr(self.pcnr, self.gh)
        self.fl_out.W = self.cmp_model.wr(self.pcnr, self.gh) * self.fl_out.pt / np.sqrt(self.fl_out.Tt)
