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
	"""
	orderlines = utils.readfile("../test/testproblem.csv")
	dists = warehouse.distance_matrix
	edges = utils.get_edges(orderlines, dists)

	solver = Solver(orderlines, edges, dists, (120, 80, 150), 450)
	sol = solver.heuristic(GREEDY_BETA)
	cost = solver.getCost(sol, dists)

	print(len(sol), cost)
	for i in sol:
		utils.plot(i)
	"""
	with open(f"../Results.csv", "w") as output_file:
		for file in benchmark.BENCHMARKS:
			problem = benchmark.read_benchmark(f"../benchmarks/{file}")


			orderlines, dists, pallet_size, max_weight = problem.orderlines, problem.dists, problem.pallet_size, problem.pallet_max_weight
			edges = utils.get_edges(orderlines, dists)

			solver = Solver(orderlines, edges, dists, pallet_size, max_weight)
			sol = solver.heuristic(GREEDY_BETA)
			cost = solver.getCost(sol, dists)
			#sol, cost, _ = solver(60)

			output_file.write(f"{problem.name}, {problem.customers}, {problem.items}, {problem.vehicles}, {len(sol)}, {cost} \n")

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
