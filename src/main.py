import multiprocessing
import functools
import operator

import warehouse
import utils
import benchmark

from solver import Solver, GREEDY_BETA



def worker (id, return_dict, orderlines, edges, dists):
	"""
	 Method to use in case of multiprocessing
	"""
	print(f"Worker {id} is digging.")
	solver = Solver(orderlines, edges, dists)
	sol, cost, iterations = solver.__call__(maxtime=180)
	return_dict[id] = iterations
	print(f"Worker {id} ended.")



if __name__ == "__main__":

	#orderlines = utils.readfile("../test/testproblem.csv")
	#dists = warehouse.distance_matrix
	#edges = utils.get_edges(orderlines, dists)

	with open(f"../Results.csv", "w") as output_file:
		for file in benchmark.BENCHMARKS:
			problem = benchmark.read_benchmark(f"../benchmarks/{file}")

			pallet_size = problem.pallet_size
			pallet_volume = functools.reduce(operator.mul, pallet_size, 1)
			pallet_area = functools.reduce(operator.mul, pallet_size[:2], 1)
			#print(f"Volume : {pallet_volume} - Area : {pallet_area} - MaxSize : {max(pallet_size[0], pallet_size[1])} - Size : {pallet_size}")

			#maxX = max(case.sizex for orderline in problem.orderlines for case in orderline.cases)
			#maxY = max(case.sizey for orderline in problem.orderlines for case in orderline.cases)
			#print(max(maxX, maxY))

			#continue

			orderlines = problem.orderlines
			dists = problem.dists
			edges = utils.get_edges(orderlines, dists)

			solver = Solver(orderlines, edges, dists, problem.pallet_size, problem.pallet_max_weight)
			#sol = solver.heuristic(GREEDY_BETA)
			#cost = solver.getCost(sol, dists)
			sol, cost, _ = solver(60)
			
			output_file.write(f"{problem.name}, {problem.customers}, {problem.vehicles}, {len(sol)}, {cost} \n")

			#for pallet in sol:
			#	utils.plot(pallet)




	# Use the following for multiprocessing
	# ---------------------------------------------------------------------------------------------------
	# manager = multiprocessing.Manager()
	# return_dict = manager.dict()
	# jobs = []
	# for i in range(4):
	# 	proc = multiprocessing.Process(target=worker, args=(i, return_dict, orderlines, edges, dists))
	# 	jobs.append(proc)
	# 	proc.start()
	#
	# for proc in jobs:
	# 	proc.join()
	#
	# print(return_dict)
	# ----------------------------------------------------------------------------------------------------
