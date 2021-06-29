import utils
import time
import packing
from pallet import Pallet

if __name__ == "__main__":
	orderlines = utils.readfile("../test/testproblem.csv")
	cases = []
	for o in orderlines:
		cases.extend(o.cases)
	pallet = Pallet()

	start = time.time()
	done = packing.dubePacker(pallet, cases)
	print(time.time() - start)
	print(done)
	pallet.cases = cases
	utils.plot(pallet)
