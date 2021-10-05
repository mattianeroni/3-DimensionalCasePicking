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
import collections


# Pallets characteristics
PALLET_SIZE = (120, 80, 150)
PALLET_MAX_WEIGHT = 450

# Define teh maximum volume capacity of a pallet
PALLET_MAX_VOLUME = PALLET_SIZE[0] * PALLET_SIZE[1] * PALLET_SIZE[2]


# Implement an hashable distionary
class HashableDict (dict):

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class Pallet (object):
    """
    An instance of this class represents a pallet.
    """
    
    def __init__ (self):
        """
        :attr layersMap: <dict<OrderLine,int>> hashmap that keeps track of the layer
                        that each orderline occupies into the pallet.
                        This is very important to understand in which order the storage
                        locations can be visited.
        :attr orderlines: <set<OrderLine>> the set of orderlines kept into this pallet.
        """
        self.size = PALLET_SIZE
        self.maxWeight = PALLET_MAX_WEIGHT
        self.cases = collections.deque()
        self.layersMap = HashableDict()
        self.orderlines = set()
        self.weight = 0
        self.volume = 0

    def __hash__ (self):
        """
        Method implemented to make the pallet hashable for caching.
        """
        return hash(self.layersMap)
