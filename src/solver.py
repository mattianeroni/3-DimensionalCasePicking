import collections
import operator
import random
import itertools
import matplotlib.pyplot as plt
from math import log
import time

from packing import dubePacker
from pallet import Pallet


def _bra (array):
    arr = list(array)
    L = len(array)
    for _ in range(L):
        idx = int(log(random.random() / (1 - random.uniform(0.1,0.3)))) % len(arr)
        yield arr.pop(idx)




class Solver (object):

    def __init__(self, orderlines, edges, dists):
        self.orderlines = orderlines
        self.edges = edges
        self.dists = dists
        self.history = collections.deque()


    def plot(self):
        plt.plot(self.history)
        plt.ylabel("Total distance")
        plt.xlabel("Iterations")
        plt.show()


    @staticmethod
    def getSol (edges, orderlines):
        pallets = []
        for orderline in orderlines:
            p = Pallet()
            done, packedCases, layersMap = dubePacker(p, list(orderline.cases))
            if not done: raise Exception("Unfeasible problem - Necessity to split order lines.")
            p.orderlines.append(orderline)
            p.cases, p.layersMap = packedCases, layersMap
            orderline.pallet = p
            pallets.append(p)

        for n, edge in enumerate(edges):
            iPallet = edge.origin.pallet
            jPallet = edge.end.pallet

            if iPallet == jPallet:
                continue

            if sum(i.weight for i in iPallet.cases) + sum(i.weight for i  in jPallet.cases) < iPallet.maxWeight:
                done, packedCases, layersMap = dubePacker(iPallet, list(jPallet.cases))

                if done:
                    iPallet.cases = packedCases
                    iPallet.layersMap = layersMap
                    iPallet.orderlines.extend(jPallet.orderlines)
                    pallets.remove(jPallet)
                    for i in jPallet.orderlines:
                        i.pallet = iPallet
                    continue


            iPallet, jPallet = jPallet, iPallet
            if sum(i.weight for i in iPallet.cases) + sum(i.weight for i in jPallet.cases) < iPallet.maxWeight:
                done, packedCases, layersMap = dubePacker(iPallet, list(jPallet.cases))
                if done:
                    iPallet.cases = packedCases
                    iPallet.layersMap = layersMap
                    iPallet.orderlines.extend(jPallet.orderlines)
                    pallets.remove(jPallet)
                    for i in jPallet.orderlines:
                        i.pallet = iPallet

        return pallets



    @staticmethod
    def getCost (pallets, dists):
        total = 0
        for pallet in pallets:
            sorted_orderlines = tuple(sorted(pallet.layersMap.items(), key=operator.itemgetter(1)).keys())
            total += dists[0, sorted_orderlines[0].location] + dists[sorted_orderlines[-1].location, 0]
            total += sum(dists[i.location, j.location] for i, j in zip(sorted_orderlines[:-1], sorted_orderlines[1:]))
        return total


    def __call__(self, maxtime):
        # Move the useful functions to the stack
        save = self.history.append
        getSol = self.getSol
        getCost = self.getCost
        # move useful data to the stack
        dists = self.dists
        edges = sorted(self.edges, key=operator.attrgetter("saving"))
        orderlines = self.orderlines
        # Generate a starting solution
        best = getSol(edges, orderlines)
        bestcost = getCost(best)
        # Multi-start iterated local search
        start = time.time()
        while time.time() - start < maxtime:
            # Generate a new solution
            newsol = getSol(edges, orderlines)
            newcost = getCost(newsol)
            # Eventually updates the best
            if newcost < bestcost:
                bestcost, bestsol = newcost, newsol

            # Store the cost of the best solution found so far
            save(bestcost)
        # Return the best solution found
        return best, bestcost
