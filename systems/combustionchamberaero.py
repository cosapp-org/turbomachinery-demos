import numpy as np

from cosapp.systems import System

from ports.fluidport import FluidPort
from utils.idealgas import IdealGas


class CombustionChamberAero(System):
    """
    Combustion Chamber aero
    fl_out FluidPort is computed from fl_in FluidPort.
    """

    def setup(self, FluidLaw = IdealGas):
        self.add_inward('gasproperty', IdealGas)

        # inputs / outputs
        self.add_input(FluidPort, 'fuel_in')
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        # inwards / outwards
        self.add_inward('eff', 0.99)
        self.add_inward('Tt_des', 1400.)

        # init
        self.fuel_in.fluid = 'C3H8'
        self.fuel_in.W = 0.01 * self.fl_in.W

        # design methods
        self.add_design_method('aero').add_equation('fl_out.Tt == Tt_des')


    def compute(self):
        # input conditions
        fuel_in = self.gasproperty(self.fuel_in.fluid, self.fl_in.pt, self.fl_in.Tt)
        gas = self.gasproperty(self.fl_in.fluid, self.fl_in.pt, self.fl_in.Tt)
        cp = gas.cp
        HHV = gas.HHV(self.fuel_in.fluid)

        # computations
        h_in = cp * self.fl_in.Tt
        h_out = h_in + self.fuel_in.W/self.fl_in.W * HHV * self.eff * 1e6

        # output conditions
        self.fl_out.fluid = self.fl_in.fluid
        self.fl_out.W = self.fl_in.W + self.fuel_in.W
        self.fl_out.pt = self.fl_in.pt
        self.fl_out.Tt = h_out / cp


