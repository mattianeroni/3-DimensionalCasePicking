import collections


# Pallets characteristics
PALLET_SIZE = (120, 80, 150)
PALLET_MAX_WEIGHT = 450


def froze (pallet):
    pallet.frozen = dict(pallet.__dict__)


class Pallet (object):
    def __init__ (self):
        self.size = PALLET_SIZE
        self.maxWeight = PALLET_MAX_WEIGHT
        self.cases = collections.deque()
        self.layersMap = dict()
        self.frozen = None

    def froze (self):
        self.frozen = dict(self.__dict__)
