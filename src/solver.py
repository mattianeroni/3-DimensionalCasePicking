import collections
import operator
import matplotlib.pyplot as plt



class Solver (object):
    def __init__(self, orderlines, edges, dists):
        self.orderlines = orderlines
        self.edges = edges
        self.dists = dists

	self.history = collections.deque()


    def plot(self):
        plt.plot(self.history)
        plt.ylabel("Total distance")
        plt.xlabel("Improvements")
        plt.show()



    @staticmethod
    def getSol ():
        pass


    @staticmethod
    def getCost (pallets, dists):
        totalcost = 0
        for pallet in pallets:
            sorted_orderlines = dict(sorted(pallet.layersMap, key=operator.itemgetter(1))).keys()
            totalcost += dists[0, sorted_orderlines[0].location] + dists[sorted_orderlines[-1].location, 0]
            totalcost += sum(dists[i.location, j.location] for i, j in zip(sorted_orderlines[:-1],sorted_orderlines[1:]))
        return totalcost


	def __call__(self, maxiter=1000):
        # Move the useful functions to the stack
		save = self.history.append
        getSol = self.getSol
        getCost = self.getCost
        # move useful data to the stack
        dists = self.dists

        # Generate a starting solution
		best = getSol()
		bestcost = getCost(best, dists)
        # Multi-start iterated local search
		for i in range(maxiter):
			newsol = getSol()
			newcost = getCost(newsol, dists)
			if newcost < bestcost:
				bestcost = newcost
				bestsol = newsol
				save(bestcost)
        # Return the best solution found
		return bestsol, bestcost
