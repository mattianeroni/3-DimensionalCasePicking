import collections

PALLET_SIZE = (200, 150, 100)#(120, 80, 100)


class Pallet (object):
    def __init__ (self):
        self.size = PALLET_SIZE
        self.cases = collections.deque()

    def __hash__ (self):
        return str(hash(self))
