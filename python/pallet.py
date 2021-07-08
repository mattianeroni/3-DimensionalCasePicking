import collections


# Pallets characteristics
PALLET_SIZE = (120, 80, 150)
PALLET_MAX_WEIGHT = 450

# Define teh maximum volume capacity of a pallet
PALLET_MAX_VOLUME = PALLET_SIZE[0] * PALLET_SIZE[1] * PALLET_SIZE[2]


class Pallet (object):
    def __init__ (self):
        self.size = PALLET_SIZE
        self.maxWeight = PALLET_MAX_WEIGHT
        self.cases = collections.deque()
        self.layersMap = dict()
        self.orderlines = set()
        self.weight = 0
        self.volume = 0

    def __hash__ (self):
        return hash(str(self))
