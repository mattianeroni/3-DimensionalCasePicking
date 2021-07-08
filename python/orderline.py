

class OrderLine (object):
    def __init__ (self, code, location, cases=None):
        self.code = code
        self.location = location
        self.cases = cases
        self.weight = 0
        self.volume = 0 

        self.pallet = None
        self.dn_edge = None
        self.nd_edge = None

    def __hash__(self):
        return hash(str(self))
