import numpy as np
import cantera as ct

from utils.idealgas import IdealGas

class CanteraFluid:

    def __init__(self, gas, p, T):
        self.gas = ct.Solution('gri30.cti')
        if gas == 'air':
            self.gas.TPX = T, p, 'N2:75.52, O2:23.14, CO2:0.051, Ar:1.29'
        else:
            self.gas.TPX = T, p, f'{gas}:1'

    def get_name(self, gas):
        name={'C10H26' : 'nDodecane_Reitz'}
        return name[gas]

    @property
    def cp(self):
        return self.gas.cp

    @property
    def gamma(self):
        return self.gas.cp / self.gas.cv

    @property
    def T(self):
        return self.gas.T

    @property
    def p(self):
        return self.gas.P

    @property
    def density(self):
        return self.gas.density

    def isentropic_from_dh(self, dh):
        tr = 1 + dh / (self.cp * self.T)
        gamma = self.gamma
        self.gas.TP = (self.T * tr, self.p * tr ** (gamma/(gamma-1)))

    def isentropic_from_pr(self, pr):
        gamma = self.gamma
        self.gas.TP = (self.T * pr ** ((gamma-1)/gamma), self.p * pr)

    def HHV(self, fuel):
        
        """ Returns the LHV and HHV for the specified fuel """
        water = ct.Water()
        # Set liquid water state, with vapor fraction x = 0
        water.TX = 298, 0
        h_liquid = water.h
        # Set gaseous water state, with vapor fraction x = 1
        water.TX = 298, 1
        h_gas = water.h

        self.gas.set_equivalence_ratio(1.0, fuel, 'O2:1.0')
        h1 = self.gas.enthalpy_mass
        Y_fuel = self.gas[fuel].Y[0]

        # complete combustion products
        Y_products = {'CO2': self.gas.elemental_mole_fraction('C'),
                    'H2O': 0.5 * self.gas.elemental_mole_fraction('H'),
                    'N2': 0.5 * self.gas.elemental_mole_fraction('N')}

        self.gas.TPX = None, None, Y_products
        Y_H2O = self.gas['H2O'].Y[0]
        h2 = self.gas.enthalpy_mass
        LHV = -(h2-h1)/Y_fuel
        HHV = -(h2-h1 + (h_liquid-h_gas) * Y_H2O)/Y_fuel
        return HHV/1e6