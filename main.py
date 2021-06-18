import utils
import copy
import time

import dubepacker
from pallet import Pallet

if __name__ == "__main__":
	orderlines = utils.readfile("./test/testproblem.csv")
	cases = []
	for o in orderlines[:5]:
		cases.extend(o.cases)
	pallet = Pallet()


	done = dubepacker.dubePacker(pallet, cases)

	print(done)
	pallet.cases = cases
	utils.plot(pallet)
