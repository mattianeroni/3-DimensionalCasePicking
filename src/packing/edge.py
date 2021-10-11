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

class Edge (object):
    """
    An instance of this class represents an edge connecting
    two different storage locations inside a warehouse.
    Since each orderline is associated with one and only one
    location, the Edge also figuratively connects two orderlines.

    """
    def __init__(self, origin, end, cost, saving, inverse=None):
        """
        Constructor.

        :param origin: <OrderLine> the origin orderline
        :param end: <OrderLine> the destination order line
        :param cost: <int> the length of the edge (i.e., distance between locations)
        :param saving: <int> the saving defined by Clarke-Wright
        :param inverse: <Edge> the inverse Edge connecting the destination to the origin.

        """
        self.origin = origin
        self.end = end
        self.cost = cost
        self.saving = saving
        self.inverse = inverse
