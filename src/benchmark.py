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
import dataclasses
import collections
import itertools
import numpy as np
from math import pow, sqrt
from typing import Any

from packing import OrderLine, Case


# Benchmark instances proposed in literature that will be used to test the
# proposed algorithm on theorical and well-known problems.
BENCHMARKS = ("3l_cvrp01.txt", "3l_cvrp02.txt", "3l_cvrp03.txt", "3l_cvrp04.txt", "3l_cvrp05.txt",
              "3l_cvrp06.txt", "3l_cvrp07.txt", "3l_cvrp08.txt", "3l_cvrp09.txt", "3l_cvrp10.txt",
              "3l_cvrp11.txt", "3l_cvrp12.txt", "3l_cvrp13.txt", "3l_cvrp14.txt", "3l_cvrp15.txt",
              "3l_cvrp16.txt", "3l_cvrp17.txt", "3l_cvrp18.txt", "3l_cvrp19.txt", "3l_cvrp20.txt",
              "3l_cvrp21.txt", "3l_cvrp22.txt", "3l_cvrp23.txt", "3l_cvrp24.txt", "3l_cvrp25.txt",
              "3l_cvrp26.txt", "3l_cvrp27.txt")


@dataclasses.dataclass(frozen=True)
class Problem (object):
    """
    An instance of this class represents a 3-Load Capacitated Vehicle Routing
    Problem (3L-CVRP) to solve.
    """
    name : str
    customers : int
    vehicles : int
    items : int
    pallet_max_weight : int
    pallet_size : tuple
    nodes : tuple
    orderlines : tuple
    dists : Any # numpy array



def _distance_matrix(nodes):
    """
    Given a set of nodes indicated as (x, y) coordinates, this
    method returns the corresponding matrix of distances
    by using Euclidean distance.
    """
    def euclidean (n1, n2):
        return int(sqrt(pow(n1[0] - n2[0], 2) + pow(n1[1] - n2[1], 2)))

    L = len(nodes)
    dists = np.zeros((L,L))
    for i, j in itertools.permutations(range(L), 2):
        dists[i, j] = euclidean(nodes[i], nodes[j])

    return dists.astype("int32")


def read_benchmark (file):
    """
    This method translates a benchmark file into a standardised
    problem instance with all the attributes needed.
    """
    name, customers, vehicles, items = 0, 0, 0, 0
    orderlines, nodes = [], []
    with open(file, "r") as file:
        for i, row in enumerate(file):
            # Read instance name
            if i == 0: name = row.split(" ")[1].replace(".dat\n","").replace(".DAT\n","")
            # Read number of customers, vehicles, and items
            if i == 2: customers = int(row.split(" --- ")[0])
            if i == 3: vehicles = int(row.split(" --- ")[0])
            if i == 4: items = int(row.split(" --- ")[0])
            # Read vahicles characteristics (i.e., in our case pallets' characteristics)
            if i == 6:
                max_weight, Z, Y, X = tuple(map(int, " ".join(row.split()).split(" ")))
            # If we are reading the nodes coordinates rows...
            if 8 <= i < 8 + customers + 1:
                # Create a node in the graph
                code, x, y, _ = tuple(map(int, map(float, " ".join(row.split()).split(" "))))
                nodes.append((x, y,))

            if i > 8 + customers + 2:
                # Get the number from the file
                id, n, *data = tuple(map(int, " ".join(row.split()).split(" ")))
                # Create new orderline for each couple customer-code
                # NOTE the proposed algorithm is designed to work in a context in which
                # each orderline require one and only one code.
                #orderline = OrderLine(code=str(id), location=id)
                # Generate cases to place into the pallets / vehicles
                #cases = collections.deque()
                for case_id in range(n):
                    pos = 4 * case_id
                    code = f"{str(id)}.{str(case_id)}"
                    orderline = OrderLine(code = code, location = id)
                    case = Case(orderline, code, data[pos + 1], data[pos + 2], data[pos + 0], weight=0, strength=10)#data[pos + 3])
                    orderline.cases = (case,)
                    orderline.weight = case.weight
                    orderline.volume = case.sizex * case.sizey * case.sizez
                    orderlines.append(orderline)
        # Return the problem with the characteristics read from the file
        return Problem(name, customers, vehicles, items, max_weight, (X,Y,Z), tuple(nodes), tuple(orderlines), _distance_matrix(nodes))
