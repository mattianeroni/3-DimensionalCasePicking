class Case (object):

    def __init__ (self, x, y, sizex, sizey, weight, height):
        self.x = x
        self.y = y
        self.sizex = sizex
        self.sizey = sizey
        self.weight = weight
        self.height = height

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
