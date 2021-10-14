"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This file is part of the implementation of an algorithm for solving the
3-dimensional case picking problem. A newly considered problem of operational
research that combines the routing of pickers into the warehouse, with the
positioning of 3-dimensional items inside pallets (i.e., Pallet Loading Problem).

The algorithm proposed and implemented comes from a collaboration between the
Department of Engineering at University of Parma (Parma, ITALY) and the
IN3 Computer Science Dept. at Universitat Oberta de Catalunya (Barcelona, SPAIN).


Written by Mattia Neroni Ph.D., Eng. in July 2021.
Author' contact: mattianeroni93@gmail.com
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

def rotate (case):
    """
    Method used to rotate a case of 90° on the horizontal plan.
    :param case: <Case> The case to rotate.
    """
    case.rotated = not case.rotated
    case.sizex, case.sizey = case.sizey, case.sizex


class Case (object):
    """
    An instance of this class represent one of the rectangular-shaped 3-dimensional cases
    to place into the pallets.
    """
    def __init__ (self, orderline, code, sizex, sizey, sizez, weight, strength):
        """
        Constructor.

        :param orderline: <OrderLine> the orderline the case belongs to
        :param code: <char> the code of the case (the type of product it contains)
        :param sizex, sizey, sizez: <int> the dimensions of the case
        :param weight: <int> the weight of the case
        :param strength: <int> the strenght of the case (i.e., the number of cases it can hold above)
        """
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
        self.busyCorners = [False, False, False]  # Used to speed up the DubePacker

    def __repr__(self):
        return f"Case(position={self.position}, size=({self.sizex}, {self.sizey}, {self.sizez})," \
                 f" weight={self.weight}, strength={self.strength}, rotated={self.rotated}, busyCorners={self.busyCorners})"

    def __copy__ (self):
        obj = Case.__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj.busyCorners = list(self.busyCorners)
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
