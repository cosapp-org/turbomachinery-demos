import numpy as np

from cosapp.systems import System
from ports.fluidport import FluidPort

from utils.idealgas import IdealGas

class InletAero(System):
    """
    Inlet aero
    """

    def setup(self):
        self.add_inward('FluidLaw', IdealGas)

        # inwards/outwards
        self.add_inward('W', 40., unit='kg/s', desc='mass flow')
        self.add_inward('ps', 101325., unit='Pa', desc='static pressure')
        self.add_inward('Ts', 293.15, unit='K', desc='static temperature')
        self.add_inward('Mach', .85, desc='Mach')

        self.add_inward('sec', 1., desc='sec')

        self.add_outward('thrust', unit='N', desc='thrust')

        # inputs / outputs
        self.add_output(FluidPort, 'fl_out')


    def compute(self):
        gas = self.FluidLaw('air', self.ps, self.Ts)
        gamma = gas.gamma

        Mach = self.Mach

        self.fl_out.fluid = 'air'
        self.fl_out.W = self.W
        r = (1 + (gamma -1)/2 * Mach ** 2)
        self.fl_out.pt = self.ps * r ** (gamma / (gamma - 1))
        self.fl_out.Tt = self.Ts * r

        self.thrust = (self.fl_out.pt - self.ps) * self.sec
