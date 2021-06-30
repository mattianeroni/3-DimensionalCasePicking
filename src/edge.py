
class Edge (object):
    def __init__(self, origin, end, cost, saving, inverse=None):
        self.origin = origin
        self.end = end
        self.cost = cost
        self.saving = saving
        self.inverse = inverse
