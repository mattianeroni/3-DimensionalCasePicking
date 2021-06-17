import utils
import copy
import time

import packer
from pallet import Pallet

if __name__ == "__main__":
	orderlines = utils.readfile("./test/testproblem.csv")
	cases = []
	for o in orderlines[:5]:
		cases.extend(o.cases)
	pallet = Pallet()

	start = time.time()
	done = packer.dubePacker(pallet, cases)
	print(time.time() - start)
	#print(len(cases))
	print(done)
	pallet.cases = cases
	utils.plot(pallet)
