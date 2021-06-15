"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                             *  3-Dimensional Case Picking  *

This file contains the implementation of OrderLine class. Each object constitute a request of customers and is
identified by a certain product code, a set of cases to pick and pack, and a location in the warehouse where cases
are stored.
Each OrderLine also represents a node in the ClarkeWright merging process.

Author: Mattia Neroni, Ph.D., Eng. (May 2021).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

"""
class OrderLine (object):

    def __init__(self, code, cases, location):
        self.code = code
        self.cases = cases
        self.location = location
        self.nd_edge = None
        self.dn_edge = None