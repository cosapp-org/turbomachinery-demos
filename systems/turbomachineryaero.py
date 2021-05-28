import numpy as np

from cosapp.systems import System

from utils.idealgas import IdealGas

from systems.compressoraero import CompressorAero
from systems.gasgeneratoraero import GasGeneratorAero
from systems.turbineaero import TurbineAero

from systems.mixeraero import MixerAero

class TurbomachineryAero(System):
    """
    Turbomachinery aero
    fl_out FluidPort is computed from fl_in FluidPort.
    """

    def setup(self):
        self.add_inward('FluidLaw', IdealGas)


        # inwards/outwards
        self.add_outward('opr_des', 50., desc='overall pressure ratio design')

        self.add_outward('bpr', desc='by pass ratio')
        self.add_outward('opr', desc='overall pressure ratio')

        # children
        self.add_child(CompressorAero('fanaero'), pulling=['fl_in'])
        self.add_child(MixerAero('bypassaero', n_in=1, n_out=2))
        self.add_child(GasGeneratorAero('gasgeneratoraero'), pulling=['fuel_in'])
        self.add_child(TurbineAero('turbineaero'))
        self.add_child(MixerAero('mergeraero', n_in=2, n_out=1), pulling={'fl0_out' : 'fl_out'})

        # primery flow
        self.connect(self.fanaero.fl_out, self.bypassaero.fl0_in)
        self.connect(self.bypassaero.fl0_out, self.gasgeneratoraero.fl_in)
        self.connect(self.gasgeneratoraero.fl_out, self.turbineaero.fl_in)
        self.connect(self.turbineaero.fl_out, self.mergeraero.fl0_in)

        # secondary flow
        self.connect(self.bypassaero.fl1_out, self.mergeraero.fl1_in)
        
        # shaft
        self.connect(self.turbineaero.shaft_out, self.fanaero.shaft_in)

        # design methods
        self.add_design_method('aero')\
            .extend(self.gasgeneratoraero.design_methods['aero'])\
            .extend(self.turbineaero.design_methods['aero'])\
            .add_equation('opr == opr_des')

        # init
        self.bypassaero.r1 = 0.9


    def compute(self):
        self.bpr = self.bypassaero.r1 / self.bypassaero.r0
        self.opr = self.gasgeneratoraero.compressoraero.fl_out.pt / self.fl_in.pt