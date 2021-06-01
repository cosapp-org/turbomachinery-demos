import numpy as np

from cosapp.systems import System

from ports.fluidport import FluidPort


class TubeAero(System):
    """
    tube aero.
    fl_out FluidPort is computed from fl_in FluidPort.
    """

    def setup(self):

        # inputs / outputs
        self.add_input(FluidPort, 'fl_in')
        self.add_output(FluidPort, 'fl_out')

        # inwards / outwards
        self.add_inward('K', 100.)


    def compute(self):
        self.fl_out.W = self.fl_in.W
        self.fl_out.pt = self.fl_in.pt - self.K * self.fl_in.W ** 2
        self.fl_out.Tt = self.fl_in.Tt

