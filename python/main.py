import multiprocessing

import warehouse
import utils

from solver import Solver



def worker (id, return_dict, orderlines, edges, dists):
	print(f"Worker {id} is digging.")
	solver = Solver(orderlines, edges, dists)
	sol, cost, iterations = solver.__call__(maxtime=180)
	return_dict[id] = iterations
	print(f"Worker {id} ended.")



if __name__ == "__main__":

	orderlines = utils.readfile("../test/testproblem.csv")
	dists = warehouse.distance_matrix
	edges = utils.get_edges(orderlines, dists)
	"""
	manager = multiprocessing.Manager()
	return_dict = manager.dict()
	jobs = []
	for i in range(4):
		proc = multiprocessing.Process(target=worker, args=(i, return_dict, orderlines, edges, dists))
		jobs.append(proc)
		proc.start()

	for proc in jobs:
		proc.join()

	print(return_dict)
	"""



	solver = Solver(orderlines, edges, dists)
	sol, cost, iterations = solver.heuristic(0.2)
	print(cost)
	for pallet in sol:
		#print("\n\n\n")
		#for orderline in pallet.orderlines:
		#	for case in orderline.cases:
		#		print(case.__dict__)
		utils.plot(pallet)

	#	#print(pallet.layersMap)

	#solver.plot()
