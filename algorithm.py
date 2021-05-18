import numpy as np
import random
import math



def biased_random_selection (lst, beta):
    """
    Given an iterable and a parameter for the quasi-geometric function,
    this generator operates a biased randomised selection yielding the 
    elements of the iterable.
    
    """
    L = len(lst); options = list(lst)
    for _ in range(L):
        idx = int(math.log(random.random(), 1 - beta)) % len(options)
        yield options.pop(idx) 