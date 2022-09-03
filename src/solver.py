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
import operator
import random
import itertools
import matplotlib.pyplot as plt
import time
from math import log

from packing import dubePacker
from packing.pallet import Pallet
from packing.case import Case, resetCase
from packing.orderline import assignPallet
import utils


# Convention value used to obtain a greedy behaviour from the
# Biased Randomised Algorithm implemented below.
# Theorically speaking the value should be as close as possible to 1.
# We have reason to believe an approximation to four decimals should
# be accurate enough.
GREEDY_BETA = 0.9999


def _bra (array, beta):
    """
    This method carry out a biased-randomised selection over a certain list.
    The selection is based on a quasi-geometric function:

                    f(x) = (1 - beta) ^ x

    and it therefore prioritise the first elements in list.

    :param array: <list> The set of options already sorted from the best to the worst.
    :param beta: <float> The parameter of the quasi-geometric distribution.
    :return: The element picked at each iteration.

    """
    arr = list(array)
    L = len(array)
    for _ in range(L):
        idx = int(log(random.random(), 1.0 - beta)) % len(arr)
        yield arr.pop(idx)



class Solver (object):
    """
    An instance of this class represents a solver for the
    3-dimensional Case Picking problem.
    """
    def __init__(self, orderlines, edges, dists, pallet_size=(120,80,150), pallet_max_weight=450):
        """
        :attr orderlines: <tuple<OrderLine>> The set of orderlines for which
                        the problem must be solved.
        :attr edges: <tuple<Edge>> The edges connecting location to each other.
        :attr dists: <numpy.array> The matrix of distances between locations.
        :attr pallet_size: <tuple<int>> Pallets size
        :attr pallet_max_weight: <int> Pallets max weight
        :attr history: The evelution of the best solution during the iterations
                        of the algorithm.

        NOTE that to each OrderLine is supposed to be associated one and only
        one location.
        """
        self.orderlines = orderlines
        self.edges = edges
        self.dists = dists
        self.pallet_size = pallet_size
        self.pallet_max_weight = pallet_max_weight
        self.history = collections.deque()


    def plot (self):
        """
        This method plots the evolution of the current best solution during the
        execution of the algorithm.
        """
        plt.plot(self.history)
        plt.xlabel("Iterations")
        plt.ylabel("Total Distance")
        plt.show()


    def destruction (self, palletsList, solutionEdges, n):
        """
        This method is used to reverse the construction of a solution.

        :param palletsList: The current solution to partially destroy.
        :param solutionEdges: The edges in the order in which they have been considered 
                               during the construction of the solution.
        :param n: The entity (i.e., number of edges) of the destruction.
        :return: The updated palletsList and solutionEdges
        """
        # Get pallets characteristics on stack
        pallet_size, pallet_max_weight = self.pallet_size, self.pallet_max_weight


        for _ in range(n):
            # Get the next edge to remove from the solution
            edge = solutionEdges.pop()

            # We get the pallet of the origin 
            # NOTE: It might be different from the pallet of the end, but we cannot 
            # save the instance of the pallet in the edge, because it would be lost 
            # after the first destruction that involve that pallet.
            pallet = edge.origin.pallet
            
            # Create two pallets from the starting one 
            newPallet1 = Pallet(pallet_size, pallet_max_weight)
            newPallet2 = Pallet(pallet_size, pallet_max_weight)

            # Define which orderlines are moved into the new pallet and 
            # removed from the previous one.
            _idx = pallet.sorted_orderlines.index(edge.origin)

            # Check in the resulting pallets are feasible
            sorted_orderlines_1 = pallet.sorted_orderlines[_idx:]
            sorted_orderlines_2 = pallet.sorted_orderlines[:_idx]

            if len(sorted_orderlines_1) <= 1 or len(sorted_orderlines_2) <= 1:
                continue

            cases_1 = tuple(resetCase(i) for or_line in sorted_orderlines_1 for i in or_line.cases)
            cases_2 = tuple(resetCase(i) for or_line in sorted_orderlines_2 for i in or_line.cases)
            done1, packedCases1, layersMap1 = dubePacker(newPallet1, cases_1)
            done2, packedCases2, layersMap2 = dubePacker(newPallet2, cases_2)

            # Eventually generates the new pallets
            if done1 and done2:
                # Update pallets characteristics
                newPallet1.sorted_orderlines = sorted_orderlines_1
                newPallet2.sorted_orderlines = sorted_orderlines_2
                newPallet1.orderlines = set(sorted_orderlines_1)
                newPallet2.orderlines = set(sorted_orderlines_2)
                newPallet1.cases = packedCases1
                newPallet2.cases = packedCases2
                newPallet1.layersMap = layersMap1
                newPallet2.layersMap = layersMap2
                newPallet1.weight = sum(i.weight for i in cases_1)
                newPallet2.weight = sum(i.weight for i in cases_2)
                newPallet1.volume = sum(i.volume for i in cases_1)
                newPallet2.volume = sum(i.volume for i in cases_2)
                [ assignPallet(orderline, newPallet1) for orderline in sorted_orderlines_1 ]
                [ assignPallet(orderline, newPallet2) for orderline in sorted_orderlines_2 ]

                # Update the list pallets 
                palletsList.remove(pallet)
                palletsList.extend([newPallet1, newPallet2])
            
        return palletsList, solutionEdges



    def heuristic (self, beta, palletsList=None, solutionEdges=None):
        """
        This method provides a single solution to the problem.

        :param beta: The parameter of the quasi-geometric distribution
                    used by the biased randomised selection.

        :param solutionEdges: The edges already used in case the solution 
                              is not constructed from scratch.

        :param palletsList: The pallets already constructed in case the 
                            solution is not constructed from scratch.

        :return: The resulting list of pallets.
        """
        # Get pallets characteristics on stack
        pallet_size, pallet_max_weight = self.pallet_size, self.pallet_max_weight

        # Build a dummy solution
        if not palletsList:
            palletsList = []
            for orderline in self.orderlines:
                p = Pallet(pallet_size, pallet_max_weight)
                done, packedCases, layersMap = dubePacker(p, orderline)
                assert done == True
                p.cases, p.layersMap = packedCases, layersMap
                p.weight = orderline.weight
                p.volume = orderline.volume
                orderline.pallet = p
                p.orderlines.add(orderline)
                p.sorted_orderlines.append(orderline)
                palletsList.append(p)

        # Save the edges in the order in which they have been considered
        solutionEdges = solutionEdges if solutionEdges else collections.deque()

        # Generate the savings list
        savingsList = sorted(
            [e for e in self.edges if e not in solutionEdges and e.inverse not in solutionEdges], 
            key=operator.attrgetter("saving"), 
            reverse=True
        )

        # Merging process
        for edge in _bra(savingsList, beta):
            # Picks an edge and read the pallet it could connect
            host = edge.origin.pallet
            hosted = edge.end.pallet

            # The the hosting pallet and the hosted pallet are the same the procedure
            # interrupts and goes to the next edge
            if host == hosted:
                continue
            # Control the volumetric lower bound
            if host.volume + hosted.volume > host.maxVolume:
                continue
            # Control the weight lower bound
            if host.weight + hosted.weight > host.maxWeight:
                continue
            # Try merging
            done, packedCases, layersMap = dubePacker(host, hosted)
            if done:
                host.cases = packedCases
                host.layersMap = layersMap
                host.weight += hosted.weight
                host.volume += hosted.volume
                host.orderlines.update(hosted.orderlines)
                host.sorted_orderlines.extend(hosted.orderlines)
                palletsList.remove(hosted)
                for line in hosted.orderlines:
                    line.pallet = host
                solutionEdges.append(edge)
                continue
            # Eventually try a merging using the inverse of the edge -- i.e., switching
            # the hositng pallet with the hosted pallet.
            host, hosted, edge = hosted, host, edge.inverse

            done, packedCases, layersMap = dubePacker(host, hosted)
            if done:
                host.cases = packedCases
                host.layersMap = layersMap
                host.weight += hosted.weight
                host.volume += hosted.volume
                host.orderlines.update(hosted.orderlines)
                host.sorted_orderlines.extend(hosted.orderlines)
                palletsList.remove(hosted)
                for line in hosted.orderlines:
                    line.pallet = host
                solutionEdges.append(edge)

        # At the end, return the palletsList
        return palletsList, solutionEdges


    @staticmethod
    def getCost(paths, dists):
        """
        Given a solution (the dictionary of paths) and the matrix of distances, this method calculates
        the cost of the solution -- i.e., the distance walked by the picker to collect all
        cases and construct the pallets.

        :param paths: The paths to carry out
        :param dists: The matrix of distances between locations
        :return: The distance walked by the picker to construct all pallets.
        """
        total = 0
        for path in paths.values():
            total += dists[0, path[0].location] + dists[path[-1].location, 0]
            total += sum(dists[i.location, j.location] for i, j in zip(path[:-1], path[1:]))
        return total


    @staticmethod
    def singlePathCost(path, dists):
        """ Like getCost but executable om a single path """
        return dists[0, path[0].location] + dists[path[-1].location, 0] + sum(dists[i.location, j.location] for i, j in zip(path[:-1], path[1:]))


    @staticmethod
    def lazy_paths(solution):
        """
        This method is the lazy way to get a path for each pallet.
        A path represents the order in which the storage locations are visited
        with respect to the order in which items have been placed on pallets.

        A path is a tuple of OrderLines in the order in which they are fulfilled.

        """
        return { 
            pallet : tuple( map(operator.itemgetter(0), sorted(pallet.layersMap.items(), key=operator.itemgetter(1))) )
                for pallet in solution
        }

    
    @staticmethod 
    def opt2_paths(solution, dists):
        """
        This method define the order in which locations must be visited 
        testing many different options through permutation.
        The order in which items must be placed on the pallet is also respected.
        """
        paths_dict = dict()

        for pallet in solution:

            orderlines_levels = sorted(pallet.layersMap.items(), key=operator.itemgetter(1))
            groups = [[i[0] for i in group] for level, group in itertools.groupby(orderlines_levels, key=operator.itemgetter(1))]
            
            currentPath = None
            currentCost = float("inf") 

            for counter, orderlines in enumerate(groups):
                L = len(orderlines)
                
                for permutated_orderlines in itertools.permutations(orderlines, L):

                    newPath = tuple(itertools.chain.from_iterable( groups[k] if k != counter else permutated_orderlines for k in range(len(groups)) ))
                    newCost = Solver.singlePathCost(newPath, dists)

                    if newCost < currentCost:
                        currentPath, currentCost = newPath, newCost
                

            paths_dict[pallet] = tuple(currentPath)

        return paths_dict

        



    def multi_start(self, maxtime, betarange=(0.1, 0.3)):
        """
         This method executes many times the heuristic method generating many
         different solutions until the available time (i.e., maxtime) is not exceeded.
         Every time a new solution is generated, it is compared with the best found so
         far, and, if better, the best solution is temporarily updated.

         :param maxtime: <time>/<float> The available computational time.
         :param betarange: The range of the parameter of the biased randomisation.

         :return: <tuple> It returns (i) the best solution found (a set of pallets),
                    (ii) the cost of the best solution (the distance made by the picker),
                    (iii) the number of solutions explored by the algorithm in the
                    available computational time.
        """
        # Move useful data to the stack
        heuristic = self.heuristic
        getCost = self.getCost
        dists = self.dists
        orderlines = self.orderlines
        save = self.history.append
        lazy_paths = self.lazy_paths   

        # Generate a starting solution and set the starting best solution
        bestSol, bestSolEdges = heuristic(GREEDY_BETA)
        bestCost = getCost( lazy_paths(bestSol) , dists)

        # Start a multistart iterated local search
        iterations = 0
        start = time.time()

        while time.time() - start < maxtime:
            iterations += 1

            beta = random.uniform(*betarange)
            newSol, _ = heuristic(beta)
            newCost = getCost( lazy_paths(newSol), dists)

            # Eventually update the best and the current
            if newCost < bestCost:
                bestSol, bestCost = newSol, newCost

            # Save the current best
            save(bestCost)

        return bestSol, bestCost, iterations


    def __call__ (self, maxtime, betarange=(0.1, 0.3), mingamma=1, gammastep=1):
        """
         This method executes many times the heuristic method generating many
         different solutions until the available time (i.e., maxtime) is not exceeded.
         Every time a new solution is generated, it is compared with the best found so
         far, and, if better, the best solution is temporarily updated.

         There is also a deconstruction process of a ceratin entity (i.e., gamma).
         Every time a new solution is generated, the previous one is destroyed 
         by reversing the mrging of <gamma> edges, and reconstructed using 
         the biased randomisation.

         :param maxtime: <time>/<float> The available computational time.
         :param betarange: The range of the parameter of the biased randomisation.
         :param mingamma: The minimum entity of the destruction process.
         :param gammastep: The increase of gamma every time a best solution is not found.

         :return: <tuple> It returns (i) the best solution found (a set of pallets),
                    (ii) the cost of the best solution (the distance made by the picker),
                    (iii) the number of solutions explored by the algorithm in the
                    available computational time.
        """
        # Move useful data to the stack
        heuristic = self.heuristic
        destruction = self.destruction
        getCost = self.getCost
        dists = self.dists
        orderlines = self.orderlines
        save = self.history.append
        lazy_paths = self.lazy_paths

        # Init the entity of the destruction process
        gamma = mingamma

        # Generate a starting solution and set the starting best solution
        bestSol, bestSolEdges = heuristic(GREEDY_BETA)
        bestCost = getCost( lazy_paths(bestSol), dists)
        currentSol, currentEdges = list(bestSol), list(bestSolEdges)
        currentCost = bestCost  

        # Start a multistart iterated local search
        iterations = 0
        start = time.time()

        while time.time() - start < maxtime:
            iterations += 1

            if gamma >= len(currentEdges):
                # New solution from scratch
                beta = random.uniform(*betarange)
                newSol, newEdges = heuristic(beta)
                newCost = getCost(lazy_paths(newSol), dists)
            else:
                # Destruction and reconstruction process...
                # Destruction process 
                destroyedSol, destroyedEdges = destruction(currentSol, currentEdges, gamma)
                # Generate a new solution
                beta = random.uniform(*betarange)
                newSol, newEdges = heuristic(beta, palletsList=destroyedSol, solutionEdges=destroyedEdges)
                newCost = getCost(lazy_paths(newSol), dists)

            # Eventually update the best and the current
            if newCost < currentCost:
                currentSol, currentEdges, currentCost = newSol, newEdges, newCost
                if newCost < bestCost:
                    bestSol, bestCost = newSol, newCost
                    gamma = mingamma 
                else:
                    gamma = min(gamma + gammastep, len(currentEdges))

            # Save the current best
            save(bestCost)

        return bestSol, bestCost, iterations


    def sequential (self):
        """
        This method provides a single solution to the problem
        by using a sequential approach --i.e., first the packing optimisation
        is carried out, and then the routing improvement is done.

        This is used to compare the proposed procedure in the __call__ method
        with a different approach where routing and packing are not solved together.
        """
        pallet_size, pallet_max_weight = self.pallet_size, self.pallet_max_weight
        palletsList = []
        # First build a pallet for each orderline (dummy solution)
        for orderline in self.orderlines:
            p = Pallet(pallet_size, pallet_max_weight)
            done, packedCases, layersMap = dubePacker(p, orderline)
            assert done == True
            p.cases, p.layersMap = packedCases, layersMap
            p.weight = orderline.weight
            p.volume = orderline.volume
            orderline.pallet = p
            p.orderlines.add(orderline)
            palletsList.append(p)

        # Sort palletsList for decreasing strength
        palletsList.sort(key=lambda i: i.cases[0].strength, reverse=True)

        # For each couple of different pallets...
        for iPallet, jPallet in itertools.permutations(palletsList, 2):
            # If both are active (have not been merged into others).
            if iPallet.active and jPallet.active:
                # Control the volumetric lower bound
                if iPallet.volume + jPallet.volume > iPallet.maxVolume:
                    continue
                # Control the weight lower bound
                if iPallet.weight + jPallet.weight > iPallet.maxWeight:
                    continue
                # Try merging
                done, packedCases, layersMap = dubePacker(iPallet, jPallet)
                if done:
                    iPallet.cases = packedCases
                    iPallet.layersMap = layersMap
                    iPallet.weight += jPallet.weight
                    iPallet.volume += jPallet.volume
                    iPallet.orderlines.update(jPallet.orderlines)
                    jPallet.active = False
                    for line in jPallet.orderlines:
                        line.pallet = iPallet
        # Remove non-active pallets
        palletsList = list(filter(operator.attrgetter("active"), palletsList))
        return palletsList
