import numpy as np

from cosapp.systems import System

from ports.fluidport import FluidPort
from ports.shaftport import ShaftPort
from utils.idealgas import IdealGas


class CompressorAero(System):
    """
    Compressor aero
    fl_out FluidPort is computed from fl_in FluidPort.
    """

    def setup(self):
        self.add_inward('gasproperty', IdealGas)

        # inputs / outputs
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        self.add_input(ShaftPort, 'shaft_in')

        # inwards / outwards
        self.add_inward('eff_is', 0.9)
        self.add_outward('Wc', unit='kg/s',desc='corrected mass flow')
        self.add_outward('Nc', unit='rpm', desc='corrected shaft speed')

        # off design
        # self.add_unknown('fl_in.W', lower_bound=0.)


    def compute(self):
        # input conditions
        fluid_in = self.fl_in.fluid
        W_in = self.fl_in.W
        Tt_in = self.fl_in.Tt
        pt_in = self.fl_in.pt

        power = self.shaft_in.power

        gas = self.gasproperty(fluid_in, pt_in, Tt_in)
        gamma = gas.gamma
        cp = gas.cp

        # computations
        delta_h = power / W_in
        Tt_out = Tt_in + delta_h / cp

        gas.isentropic_from_dh(delta_h * self.eff_is)
        pt_out = gas.p

        # output conditions
        self.fl_out.fluid = fluid_in
        self.fl_out.W = W_in
        self.fl_out.pt = pt_out
        self.fl_out.Tt = Tt_out

        # outwards
        self.Wc = self.fl_in.W * np.sqrt(self.fl_in.Tt/273.15) / (self.fl_in.pt/101325.) 
        self.Nc = self.shaft_in.N / np.sqrt(self.fl_in.Tt/273.15) 
