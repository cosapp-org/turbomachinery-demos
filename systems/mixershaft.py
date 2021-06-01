import numpy as np

from cosapp.systems import System

from ports.shaftport import ShaftPort


class MixerShaft(System):
    """
    """

    def setup(self, n_in = 1, n_out=1):
        self.add_property('n_in', n_in)
        self.add_property('n_out', n_out)

        # inputs / outputs
        for n in range(n_in):
            self.add_input(ShaftPort, f'shaft{n}_in')

        for n in range(n_out):
            self.add_output(ShaftPort, f'shaft{n}_out')

        # inwards / outwards
        for n in range(n_out):
            self.add_inward(f'r{n}', 1. / n_out)

        self.add_outward('N', unit='rpm')
        self.add_outward('power', unit='W')

        # solver
        for n in range(1, n_in):
            self.add_equation(f'shaft{n}_in.N == N')

        for n in range(1, n_out):
            self.add_unknown(f'r{n}', lower_bound=0., upper_bound=1., max_rel_step=0.1)


    def compute(self):
        n_in = self.n_in
        n_out = self.n_out

        # input conditions
        power_tot = self.shaft0_in.power
        Npower_tot = self.shaft0_in.power * self.shaft0_in.N

        for n in range(1, n_in):
            shaft = self[f'shaft{n}_in']
            power = shaft.power

            power_tot += power
            Npower_tot += power * shaft.N
        
        self.power = power_tot
        self.N = Npower_tot / power_tot

        # output conditions
        self.r0 = 1.
        for n in range(1, n_out):
            self.r0 -= self[f'r{n}']

        for n in range(n_out):
            self[f'shaft{n}_out'].power = power_tot * self[f'r{n}']
            self[f'shaft{n}_out'].N = self.N

