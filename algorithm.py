import numpy as np
import random
import math



def biased_random_selection (lst, beta):
    L = len(lst); options = list(lst)
    for _ in range(L):
        idx = int(math.log(random.random(), 1 - beta)) % len(options)
        yield options.pop(idx) 