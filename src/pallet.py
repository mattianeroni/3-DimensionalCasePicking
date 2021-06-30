import collections

PALLET_SIZE = (200, 150, 200)#(120, 80, 200)


def froze (pallet):
    pallet.frozen = dict(pallet.__dict__)


class Pallet (object):
    def __init__ (self):
        self.size = PALLET_SIZE
        self.cases = collections.deque()
        self.layers_dict = dict()
        self.frozen = None
