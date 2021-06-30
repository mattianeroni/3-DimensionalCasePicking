import utils
import time
import packing
import random
from pallet import Pallet

if __name__ == "__main__":
	orderlines = utils.readfile("../test/testproblem.csv")
	cases = []
	for o in orderlines:
		cases.extend(o.cases)
	pallet = Pallet()


	#print(hash(pallet))
	#pallet.cases.append(223)
	#print(hash(pallet))

	for _ in range(1000):
		start = time.time()
		c = random.sample(cases, 50)
		
		done = packing.dubePacker(pallet, c)
		print(time.time() - start)
	#print(done)
	pallet.cases = cases
	utils.plot(pallet)
