import numpy as np

from cosapp.systems import System

from ports.fluidport import FluidPort
from ports.shaftport import ShaftPort
from utils.idealgas import IdealGas


class TurbineAero(System):
    """
    Turbine aero
    fl_out FluidPort is computed from fl_in FluidPort.
    """

    def setup(self):
        self.add_inward('gasproperty', IdealGas)

        # inputs / outputs
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        self.add_output(ShaftPort, 'shaft_out')

        # inwards / outwards
        self.add_inward('eff_is', 0.9)
        self.add_inward('pr', 5.)

        # design methods
        self.add_design_method('aero').add_unknown('pr')


    def compute(self):
        # input conditions
        fluid_in = self.fl_in.fluid
        W_in = self.fl_in.W
        Tt_in = self.fl_in.Tt
        pt_in = self.fl_in.pt

        gas_in = self.gasproperty(fluid_in, pt_in, Tt_in)
        gamma = gas_in.gamma
        cp_in = gas_in.cp

        pr = self.pr

        # computations
        pt_out = pt_in / pr
        Tt_out_is = Tt_in * pr ** (-(gamma-1)/gamma)
        delta_h_is = cp_in * (Tt_in - Tt_out_is)
        delta_h = delta_h_is / self.eff_is
        Tt_out = Tt_in - delta_h / cp_in

        # outputs
        self.shaft_out.power = delta_h * W_in

        self.fl_out.fluid = self.fl_in.fluid
        self.fl_out.W = W_in
        self.fl_out.pt = pt_out
        self.fl_out.Tt = Tt_out