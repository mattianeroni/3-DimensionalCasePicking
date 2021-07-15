import collections
import operator
import random
import matplotlib.pyplot as plt
import time

from math import log


from packing import dubePacker
from packing import Pallet, PALLET_MAX_WEIGHT, PALLET_MAX_VOLUME



GREEDY_BETA = 0.9999


def _bra (array, beta):
    arr = list(array)
    L = len(array)
    for _ in range(L):
        idx = int(log(random.random(), 1.0 - beta)) % len(arr)
        yield arr.pop(idx)



class Solver (object):
    def __init__(self, orderlines, edges, dists):
        self.orderlines = orderlines
        self.edges = edges
        self.dists = dists
        self.history = collections.deque()


    def plot (self):
        plt.plot(self.history)
        plt.xlabel("Iterations")
        plt.ylabel("Total Distance")
        plt.show()


    def heuristic (self, beta):
        # Build a dummy solution
        palletsList = []
        for orderline in self.orderlines:
            cases = orderline.cases
            p = Pallet()
            done, packedCases, layersMap = dubePacker(p, orderline)
            assert done == True
            p.cases, p.layersMap = packedCases, layersMap
            p.weight = orderline.weight
            p.volume = orderline.volume
            orderline.pallet = p
            p.orderlines.add(orderline)
            palletsList.append(p)

        # Generate the savings list
        savingsList = sorted(self.edges, key=operator.attrgetter("saving"), reverse=True)

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
            if host.volume + hosted.volume > PALLET_MAX_VOLUME:
                continue
            # Control the weight lower bound
            if host.weight + hosted.weight > PALLET_MAX_WEIGHT:
                continue
            # Try merging
            done, packedCases, layersMap = dubePacker(host, hosted)
            if done:
                host.cases = packedCases
                host.layersMap = layersMap
                host.weight += hosted.weight
                host.volume += hosted.volume
                host.orderlines.update(hosted.orderlines)
                palletsList.remove(hosted)
                for line in hosted.orderlines:
                    line.pallet = host
                continue
            # Eventually try a merging using the inverse of the edge -- i.e., switching
            # the hositng pallet with the hosted pallet.
            host, hosted = hosted, host
            done, packedCases, layersMap = dubePacker(host, hosted)
            if done:
                host.cases = packedCases
                host.layersMap = layersMap
                host.weight += hosted.weight
                host.volume += hosted.volume
                host.orderlines.update(hosted.orderlines)
                palletsList.remove(hosted)
                for line in hosted.orderlines:
                    line.pallet = host

        # At the end, return the palletsList
        return palletsList


    @staticmethod
    def getCost(solution, dists):
        total = 0
        for pallet in solution:
            sort_orderlines = tuple(dict(sorted(pallet.layersMap.items(), key=operator.itemgetter(1))).keys())
            total += dists[0, sort_orderlines[0].location] + dists[sort_orderlines[-1].location, 0]
            total += sum(dists[i.location, j.location] for i, j in zip(sort_orderlines[:-1], sort_orderlines[1:]))
        return total


    def __call__ (self, maxtime):
        # Move useful data to the stack
        heuristic = self.heuristic
        getCost = self.getCost
        dists = self.dists
        orderlines = self.orderlines
        save = self.history.append
        # Generate a starting solution
        best = heuristic(GREEDY_BETA)
        bestcost = getCost(best, dists)
        # Start a multistart iterated local search
        iterations = 0
        start = time.time()
        while time.time() - start < maxtime:
            iterations += 1
            # Generate a new solution
            beta = random.uniform(0.1, 0.3)
            newsol = heuristic(beta)
            newcost = getCost(newsol, dists)

            # Eventually update the best
            if newcost < bestcost:
                best, bestcost = newsol, newcost
            # Save the current best
            save(bestcost)

        return best, bestcost, iterations
