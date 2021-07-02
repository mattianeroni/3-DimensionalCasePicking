
import time
import operator


import packing
import warehouse
import utils

from pallet import Pallet
from solver import Solver






if __name__ == "__main__":
	orderlines = utils.readfile("../test/testproblem.csv")
	dists = warehouse.distance_matrix
	edges = utils.get_edges(orderlines, dists)

	solver = Solver(orderlines, edges, dists)
	start = time.time()
	sol, cost = solver.__call__(maxtime=60)
	print(time.time() - start)

	print(cost)
	for pallet in sol:
		utils.plot(pallet)

	solver.plot()
