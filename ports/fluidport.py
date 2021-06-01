from cosapp.ports import Port


class FluidPort(Port):
    
    def setup(self):
        self.add_variable("W", 1., unit="kg/s")
        self.add_variable("pt", 101325., unit="Pa")
        self.add_variable("Tt", 288.15, unit="K")
