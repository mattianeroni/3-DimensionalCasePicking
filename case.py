from matplotlib.patches import Rectangle


def rotate (case):
    case.sizex, case.sizey = case.sizey, case.sizex



class Case (object):

    def __init__ (self, x, y, sizex, sizey, weight, height):
        self.x = x
        self.y = y
        self.sizex = sizex
        self.sizey = sizey
        self.weight = weight
        self.height = height

    def __hash__(self):
        return hash(self)

    @property
    def top (self):
        return self.y + self.sizey

    @property
    def right (self):
        return self.x + self.sizex

    @property
    def left (self):
        return self.x

    @property
    def down (self):
        return self.y

    @property
    def image (self):
        return Rectangle((self.x,self.y), self.sizex, self.sizey)

    def rotate (self):
        self.sizex, self.sizey = self.sizey, self.sizex
