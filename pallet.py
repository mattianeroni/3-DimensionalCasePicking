"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                             *  3-Dimensional Case Picking  *
This file contains the pallet class.

Author: Mattia Neroni, Ph.D., Eng. (May 2021).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

# Pallet size in centimetres
PALLET_SIZE = (120, 80, 100)

class Pallet (object):
    def __init__(self):
        self.size = PALLET_SIZE
        self.cases = list()
        self.spaces = list()    # Used by some packing algorithms