import numpy as np

from cosapp.systems import System

from utils.idealgas import IdealGas

from systems.turbomachineryaero import TurbomachineryAero
from systems.inletaero import InletAero
from systems.nozzleaero import NozzleAero


class IPPSAero(System):
    """
    IPPS aero
    """

    def setup(self, TmAero=TurbomachineryAero):
        self.add_inward('FluidLaw', IdealGas)

        # inward / outwrad
        self.add_inward('thrust_des', 26000, unit='N', desc='thrust design')
        self.add_inward('bpr_des', 4., desc='bpr design')
        self.add_outward('tsfc', unit='kg/(N*h)', desc='thrust specific fuel consumption')
        self.add_outward('thrust', unit='N', desc='thrust')

        # children
        self.add_child(InletAero('inletaero'), 
            pulling={'W' : 'W', 'ps' : 'ps', 'Ts' : 'Ts', 'Mach' : 'Mach', 'thrust' : 'thrust_inlet'})
        self.add_child(TmAero('turbomachineryaero'), pulling=['fuel_in', 'bpr', 'opr'])
        self.add_child(NozzleAero('nozzleaero'), pulling={'ps' : 'ps', 'thrust' : 'thrust_nozzle'})

        # connector
        self.connect(self.inletaero.fl_out, self.turbomachineryaero.fl_in)
        self.connect(self.turbomachineryaero.fl_out, self.nozzleaero.fl_in)
        
        # off design
        self.add_unknown('W')

        # design methods
        self.add_design_method('aero')\
            .extend(self.turbomachineryaero.design_methods['aero'])\
            .extend(self.nozzleaero.design_methods['aero'])\
            .add_unknown('fuel_in.W')\
            .add_equation('thrust == thrust_des')\
            .add_equation('bpr == bpr_des')


    def compute(self):
        self.thrust = self.thrust_nozzle - self.thrust_inlet
        self.tsfc = self.fuel_in.W/self.thrust * 3600