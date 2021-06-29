

class OrderLine (object):
    def __init__ (self, code, location, cases):
        self.code = code
        self.location = location
        self.cases = cases
        self.layer = 0

        self.dn_edge = None
        self.nd_edge = None
