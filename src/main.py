import utils
import time
import packing
import warehouse
from pallet import Pallet







if __name__ == "__main__":
	orderlines = utils.readfile("./test/testproblem.csv")
	dists = warehouse.distance_matrix
	edges = utils.get_edges(orderlines, dists)

	"""
	cases = []
	for o in orderlines[:7]:
		cases.extend(o.cases)
	pallet = Pallet()

	start = time.time()
	done, packedCases, layersMap = packing.dubePacker(pallet, cases)
	print(time.time() - start)
	print(done)
	print(layersMap)

	if done:
		pallet.cases = packedCases
		utils.plot(pallet)
	"""
