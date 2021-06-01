from cosapp.ports import Port


class ShaftPort(Port):
    
    def setup(self):
        self.add_variable("power", 1e6, unit="W")
        self.add_variable("N", 5000., unit="rpm")
