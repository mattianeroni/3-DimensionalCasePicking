
def rotate (case):
    case.rotated = not case.rotated
    case.sizex, case.sizey = case.sizey, case.sizex



def froze(case):
    case.frozen = dict(case.__dict__)


class Case (object):

    def __init__ (self, sizex, sizey, sizez, weight, strength, rotated=False):
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
        self.level = 0
        self.pallet = None

        self.frozen = None


    def __hash__ (self):
        return str(hash(self))

    def __repr__(self):
        return f"Case(position={self.position}, size=({self.sizex}, {self.sizey}, {self.sizez}), rotated={self.rotated}, level={self.level})"

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def rotate (self):
        self.rotated = not self.rotated
        self.sizex, self.sizey = self.sizey, self.sizex

    def froze (self):
        self.frozen = dict(self.__dict__)

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
