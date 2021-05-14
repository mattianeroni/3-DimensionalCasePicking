

class Layer (object):

    def __init__ (self, sizex, sizey):
        self.sizex = sizex
        self.sizey = sizey
        self.items = None

    @property
    def size (self):
        return self.sizex, slef.sizey
