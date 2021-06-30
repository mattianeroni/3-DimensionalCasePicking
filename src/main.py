import utils
import time
import packing
from pallet import Pallet

if __name__ == "__main__":
	orderlines = utils.readfile("./test/testproblem.csv")
	cases = []
	for o in orderlines:
		cases.extend(o.cases)
	pallet = Pallet()


	#print(hash(pallet))
	#pallet.cases.append(223)
	#print(hash(pallet))
	start = time.time()
	done, packedCases, layersMap = packing.dubePacker(pallet, cases)
	print(time.time() - start)
	print(done)
	pallet.cases = cases
	utils.plot(pallet)
