import numpy as np

from cosapp.systems import System

from utils.idealgas import IdealGas

from systems.compressoraero import CompressorAero
from systems.combustionchamberaero import CombustionChamberAero
from systems.turbineaero import TurbineAero


class GasGeneratorAero(System):
    """
    GasGenerator aero
    fl_out FluidPort is computed from fl_in FluidPort.
    """

    def setup(self):
        self.add_inward('FluidLaw', IdealGas)

        # children
        self.add_child(CompressorAero('compressoraero'), pulling=['fl_in'])
        self.add_child(CombustionChamberAero('combustionchamberaero'), pulling=['fuel_in'])
        self.add_child(TurbineAero('turbineaero'), pulling=['fl_out'])

        self.connect(self.compressoraero.fl_out, self.combustionchamberaero.fl_in)
        self.connect(self.combustionchamberaero.fl_out, self.turbineaero.fl_in)
        self.connect(self.turbineaero.shaft_out, self.compressoraero.shaft_in)

        # design methods
        self.add_design_method('aero')\
            .extend(self.combustionchamberaero.design_methods['aero'])\
            .extend(self.turbineaero.design_methods['aero'])\
