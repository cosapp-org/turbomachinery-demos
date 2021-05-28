import numpy as np

from cosapp.systems import System

from ports.fluidport import FluidPort
from ports.shaftport import ShaftPort
from utils.simplifiedmftcompressor import SimplifiedMftCompressor
from utils.idealgas import IdealGas


class CompressorMft(System):
    """
    Compressor aero from Map Fitting Tool methodology.
    fl_out FluidPort is computed from fl_in FluidPort.
    """

    def setup(self):

        # inputs / outputs
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        self.add_input(ShaftPort, 'shaft_in')

        # inwards / outwards
        self.add_inward('pcnr', 90.)
        self.add_inward('gh', 0.)
        self.add_inward('cmp_model', SimplifiedMftCompressor())
        self.add_inward('gas', IdealGas("air"))

        self.add_outward('eff_is', 0.9)
        self.add_outward('power', 1e6, unit='W', desc='power absorbed by compressor')

        # offdesign
        self.add_unknown('gh', lower_bound=0., upper_bound=1., max_rel_step=0.9)
        self.add_equation('shaft_in.power == power')


    def compute(self):
        pcnr = self.pcnr
        gh = self.gh

        self.eff_is = self.cmp_model.eff_is(pcnr, gh)

        self.fl_out.Tt = self.gas.t_from_h(self.gas.h(self.fl_in.Tt) + self.cmp_model.ghr(gh))
        self.fl_out.pt = self.fl_in.pt * self.cmp_model.pr(pcnr, gh)
        self.fl_out.W = self.cmp_model.wr(pcnr, gh) * self.fl_out.pt / np.sqrt(self.fl_out.Tt)

        self.power = self.cmp_model.ghr(gh) * self.fl_out.W

        print('wr', self.cmp_model.wr(pcnr, gh))