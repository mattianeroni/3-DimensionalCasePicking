"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                             *  3-Dimensional Case Picking  *
This file contains the implementation of case class. Each case represents one of the 3-dimensional items to pick and
place into the pallets.

Author: Mattia Neroni, Ph.D., Eng. (May 2021).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""

def rotate (case):
    case.sizex, case.sizey = case.sizey, case.sizex
    case.rotated = not case.rotated


def froze (case):
    case.assigned_position = case.position
    case.assigned_rotation = case.rotated


class Case (object):

    def __init__(self, sizex, sizey, sizez, weight, strength):
        self.position = (0,0,0)
        self.sizex = sizex
        self.sizey = sizey
        self.sizez = sizez
        self.weight = weight
        self.strength = strength

        self.rotated = False
        self.pallet = None
        self.assigned_position = None
        self.assigned_rotation = None
        self.layer = 0
        

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return f"Case(x={self.x}, y={self.y}, z={self.z}, sizex={self.sizex}, sizey={self.sizey}, sizez={self.sizez}, weight={self.weight})"

    def rotate(self):
        self.sizex, self.sizey = self.sizey, self.sizex
        self.rotated = not self.rotated

    def froze(self):
        self.assigned_position = self.position
        self.assigned_rotation = self.rotated

    @property
    def back(self):
        return self.y + self.sizey

    @property
    def front(self):
        return self.y

    @property
    def right(self):
        return self.x + self.sizex

    @property
    def left(self):
        return self.x

    @property
    def top (self):
        return self.z + self.sizez

    @property
    def bottom (self):
        return self.z
