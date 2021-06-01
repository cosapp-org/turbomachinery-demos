from logging import raiseExceptions
import numpy as np


class IdealGas:

    def __init__(self, gas, p, T):
        R = 8314. # J / (K * mol)

        M_list = {'air' : 29., 'O2' : 32., 'N2' : 28., 'CO2' : 44., 'C3H8' : 44., 'C10H26' : 146.}
        gamma_list = {'air' : 7/5, 'O2' : 7/5, 'N2' : 7/5, 'CO2' : 1.3, 'C3H8' : 75/68, 'C10H26' : 1.3}
        
        if type(gas) is dict:
            frac_tot = sum(frac for _, frac in gas.items())
            M = sum(frac * M_list[gas] for gas, frac in gas.items())/frac_tot
            cv = sum(frac * R/M_list[gas] / (gamma_list[gas] - 1) for gas, frac in gas.items())/frac_tot
            cp = sum(frac * R/M_list[gas] * gamma_list[gas] / (gamma_list[gas] - 1) for gas, frac in gas.items())/frac_tot
            gamma = cp / cv
        elif type(gas) is str:
            M = M_list[gas]
            gamma = gamma_list[gas]
            cp = R / M * gamma / (gamma - 1)

        self._cp = cp
        self._gamma = gamma
        self._r = R / M 
        self._TP = (T, p)

    @property
    def p(self):
        return self._TP[1]

    @property
    def T(self):
        return self._TP[0]
    
    @property
    def density(self):
        return self.p/(self._r * self.T)

    @property
    def cp(self):
        return self._cp

    @property
    def gamma(self):
        return self._gamma

    @property
    def h(self):
        return self.cp * self.p

    @property
    def phi(self):
        return self.cp * np.log(self.T)

    def isentropic_from_dh(self, dh):
        tr = 1 + dh / (self.cp * self.T)
        gamma = self.gamma
        self._TP = (self.T * tr, self.p * tr ** (gamma/(gamma-1)))

    def isentropic_from_pr(self, pr):
        gamma = self.gamma
        self._TP = (self.T * pr ** ((gamma-1)/gamma), self.p * pr)

    def pr(self, t1, t2, eff_poly):
        return np.exp(np.log(t2 / t1) * eff_poly * self.cp / self.r)

    def eff_poly(self, p1, t1, p2, t2):
        return self.r * np.log(p2 / p1) / (self.phi(t2) - self.phi(t1))

    def HHV(self, fuel):
        """ Returns the LHV and HHV for the specified fuel """
        HHV_list = {'C12H26' : 47.8, 'H2' : 141.8, 'C3H8' : 50.35, 'C10H26' : 48.}

        return HHV_list[fuel]