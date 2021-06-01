import numpy as np

from cosapp.systems import System
from ports.fluidport import FluidPort

from utils.idealgas import IdealGas

class NozzleAero(System):
    """
    Nozzle aero
    """

    def setup(self):
        self.add_inward('FluidLaw', IdealGas)

        # inwards/outwards
        self.add_inward('sec', 1., unit='m**2', desc='section')
        self.add_inward('ps', 101325., unit='Pa', desc='static pressure')

        self.add_outward('W', unit='kg/s')
        self.add_outward('thrust', unit='N')

        # inputs / outputs
        self.add_input(FluidPort, 'fl_in')

        # solver
        self.add_unknown('fl_in.W')
        self.add_equation('W == fl_in.W')

        # design methods
        self.add_design_method('aero')\
            .add_unknown('sec')


    def compute(self):
        gas = self.FluidLaw(self.fl_in.fluid, self.fl_in.pt, self.fl_in.Tt)
        gamma = gas.gamma
        ps = self.ps 

        pt_ratio = self.fl_in.pt / ps 
        r = pt_ratio ** ((gamma-1)/gamma)       # 1 + (gamma-1)/2 * M**2
        rho = gas.density * r ** (1 - gamma)

        Mach = np.sqrt(r ** (2/(gamma-1))-1)
        V = Mach * np.sqrt(gamma * ps / rho)

        self.W = rho * V * self.sec
        self.thrust = (self.fl_in.pt - self.ps) * self.sec

