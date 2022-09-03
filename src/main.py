import multiprocessing
import functools
import operator
import pandas as pd
import time 

import warehouse
import utils
import benchmark

from solver import Solver, GREEDY_BETA
from packing.pallet import PALLET_SIZE, PALLET_MAX_WEIGHT


def _worker (id, return_dict, problem, maxtime=3600, betas=(0.3,0.6), opt=True):
    print(f"Worker {id} is digging.")
    orderlines, dists, pallet_size, max_weight = problem.orderlines, problem.dists, problem.pallet_size, problem.pallet_max_weight
    edges = utils.get_edges(orderlines, dists)
    solver = Solver(orderlines, edges, dists, pallet_size, max_weight)
    sol, cost, iterations = solver.multi_start(maxtime, betas)
    if opt:
        paths_dict = solver.opt2_paths(sol, dists)
        cost = solver.getCost(paths_dict, dists)
    return_dict[id] = (sol, cost, iterations)
    print(f"Worker {id} ended.")



def _evaluateCurrentSol (df, dists):
    df["Volume"] = df["SizeX"] * df["SizeY"] * df["SizeZ"]
    df["MaxWeight"] = df["Weight"] * df["#Cases"]
    df["MaxVolume"] = df["Volume"] * df["#Cases"]
    df_pallets = df.groupby("PalletID").sum()
    n_pallets = df_pallets.index.__len__()
    maxweight = df_pallets["MaxWeight"].max()
    maxvolume = df_pallets["MaxVolume"].max()

    current_loc = 0
    current_pallet = None
    distance = 0

    for pallet, loc in zip(df["PalletID"], df["Location"]):

        if current_pallet is not None and pallet != current_pallet:
            distance += dists[current_loc, 0]
            current_loc = 0

        distance += dists[current_loc, loc]
        current_pallet = pallet
        current_loc = loc

    distance += dists[current_loc, 0]

    return n_pallets, distance, maxweight, maxvolume


def real_test ():
    """
    Tests made with real data.
    """
    dists = warehouse.distance_matrix
    #locations = list(range(dists.shape[0]))
    with open(f"../RealCaseResults.csv", "w") as output_file:
        # C: Current algorithm implemented by the company
        # P: Proposed algorithm
        # S: The sequential solution (i.e., packing first, routing next)
        output_file.write("TestID, #Orderlines, #Cases, #Pallets_C, Distance_C, MaxVolume_C, MaxWeight_C, #Pallets_P, Distance_P, MaxVolume_P, MaxWeight_P, #Pallets_S, Distance_S, MaxVolume_S, MaxWeight_S\n")
        for i in range(1, 22):
            print("Test ", i, end="...")
            filename = f"../tests/test{str(i)}.csv"

            # Extraction of usefull data.
            orderlines = utils.readfile(filename, delimiter=',')
            edges = utils.get_edges(orderlines, dists)

            # Get the result of the proposed algorithm.
            solver = Solver(orderlines, edges, dists, (140, 110, 150), 1200)
            sol, cost, iterations = solver.multi_start(maxtime=300)

            # Get the results of the sequential procedure where
            # we do the packing first and the routing next.
            seqsolver = Solver(orderlines, edges, dists, (140, 110, 150), 1200)
            seqsol = seqsolver.sequential()
            seqcost = seqsolver.getCost(seqsol, dists)

            # Get the results of the company.
            palletsC, costC, maxweightC, maxvolumeC = _evaluateCurrentSol(pd.read_csv(filename, index_col = "Unnamed: 0"), dists)

            # Print results
            output_file.write(f"{i}, {len(orderlines)}, {sum(len(orderline.cases) for orderline in orderlines)}, {palletsC}, {costC}, {maxvolumeC}, {maxweightC}, {len(sol)}, {cost}, {max(p.volume for p in sol)}, {max(p.weight for p in sol)}, {len(seqsol)}, {seqcost}, {max(p.volume for p in seqsol)}, {max(p.weight for p in seqsol)}\n")
            print("done")





def literature_test ():
    """
    The tests made on literature benchmarks.
    """
    with open(f"../SingleThreadLiteratureResults.csv", "w") as output_file:
        for file in benchmark.BENCHMARKS[:1]:
            problem = benchmark.read_benchmark(f"../benchmarks/{file}")
            #print(problem.name, end="...")
            
            orderlines, dists, pallet_size, max_weight = problem.orderlines, problem.dists, problem.pallet_size, problem.pallet_max_weight
            edges = utils.get_edges(orderlines, dists)

            solver = Solver(orderlines, edges, dists, pallet_size, max_weight)

            sol, cost, iterations = solver.multi_start(60, (0.3, 0.6))

            #_start = time.time() 
            paths_dict = solver.opt2_paths(sol, dists)
            cost = solver.getCost(paths_dict, dists)
            #duration = time.time() - _start

            print(len(sol), cost)
            
            
            output_file.write(
                f"{problem.name}, {problem.customers}, {problem.items}, {problem.vehicles}, {len(sol)}, {cost} \n")
            #print("done")



def literature_multiprocess_test ():
    """
    The tests made on literature benchmarks.
    """
    # Clear the file 
    #file = open(f"../LiteratureResults.csv", "w")
    #file.close()

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    jobs = []

    for filename in benchmark.BENCHMARKS:
        

        problem = benchmark.read_benchmark(f"../benchmarks/{filename}")

        maxtime = 3600
        betas = (0.3, 0.6)

        proc = multiprocessing.Process(
            target=_worker, 
            args=(filename, return_dict, problem, maxtime, betas)
        )
        jobs.append(proc)
        proc.start()


    for proc in jobs:
        proc.join()
    
    with open(f"../LiteratureResults.csv", "w") as output_file:
        
        for name, res in sorted(return_dict.items(), key=operator.itemgetter(0)):
            sol, cost, iterations = res
            output_file.write(f"{name}, {len(sol)}, {cost} \n")



if __name__ == "__main__":
    #real_test()
    #literature_test()
    literature_multiprocess_test()
