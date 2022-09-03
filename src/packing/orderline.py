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

def assignPallet(orderline, pallet):
    """
    Function that could be used to assign a pallet to
    a orderline.

    :param orderline: The orderline 
    :param pallet: The pallet
    """
    orderline.pallet = pallet
    return orderline


class OrderLine (object):
    """
    An instance of this class represents a customer orderline.

    """
    def __init__ (self, code, location, cases=None):
        """
        Constructor.
        :param code: <char> the type of product required
        :param location: <int> the unique id of the storage location where the required product is stored.
        :param cases: <list<Case>> the cases required.

        """
        self.__i = 0            # Counter used to iterate the pallet cases
        self.code = code
        self.location = location
        self.cases = cases
        self.weight = 0
        self.volume = 0

        self.pallet = None
        self.dn_edge = None
        self.nd_edge = None

    #def __repr__(self):
    #    return f"OrderLine(code={self.code}, cases={len(self.cases)}, location={self.location})"

    def __hash__(self):
        """
        Method implemented to make the OrderLine hashable. This is needed for caching
        and for using the orderlines as keys in a dictionary.
        """
        return hash(str(self))

    def __lt__(self, other):
        """
        The hashable orderlines must also be sortable. This is needed
        for caching using orderlines as keys.
        """
        return self.code < other.code

    def __iter__(self):
        self.__i = 0
        return self 


    def __next__(self):
        if self.__i < len(self.cases):
            self.__i += 1
            return self.cases[self.__i - 1]
        raise StopIteration