import utils
import time
import packing
from pallet import Pallet

if __name__ == "__main__":
	orderlines = utils.readfile("./test/testproblem0.csv")
	cases = []
	for o in orderlines:
		cases.extend(o.cases)
	pallet = Pallet()

	#print(cases)
	start = time.time()
	done = packing.dubePacker(pallet, cases)
	print(time.time() - start)
	print(done)
	pallet.cases = cases
	utils.plot(pallet)
