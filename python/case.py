
def rotate (case):
    case.rotated = not case.rotated
    case.sizex, case.sizey = case.sizey, case.sizex


class Case (object):

    def __init__ (self, orderline, code, sizex, sizey, sizez, weight, strength, rotated=False):
        self.orderline = orderline
        self.code = code
        self.x = 0
        self.y = 0
        self.z = 0
        self.rotated = False
        self.sizex = sizex
        self.sizey = sizey
        self.sizez = sizez
        self.weight = weight
        self.strength = strength
        self.canHold = strength
        #self.pallet = None
        self.busyCorners = [False, False, False]  # Used to speed up the DubePacker
        #self.frozen = None

    def __repr__(self):
        return f"Case(position={self.position}, size=({self.sizex}, {self.sizey}, {self.sizez}), rotated={self.rotated}, busyCorners={self.busyCorners})"

    def __copy__ (self):
        obj = Case.__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj.busyCorners = list(self.busyCorners)
        obj.orderline = self.orderline
        return obj

    @property
    def position (self):
        return self.x, self.y, self.z

    def setPosition(self, pos):
        self.x, self.y, self.z = pos

    @property
    def top (self):
        return self.z + self.sizez

    @property
    def bottom (self):
        return self.z

    @property
    def left (self):
        return self.x

    @property
    def right (self):
        return self.x + self.sizex

    @property
    def front (self):
        return self.y

    @property
    def back (self):
        return self.y + self.sizey
