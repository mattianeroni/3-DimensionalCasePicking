import functools
import random
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt


cachesize = 126


def test (algorithm, cases, layersize, plotsize=(10,6)):
    suc = algorithm(cases, layersize)
    if not suc:
        print("Unsuccesful packing.")
    else:
        _, ax = plt.subplots()
        ax.add_patch(Rectangle((0,0), 1, 1,linewidth=3, edgecolor='r', facecolor='none'))
        for case in cases:
            ax.add_patch(Rectangle( (case.x/layersize[0], case.y/layersize[1]),
                                    case.sizex/layersize[0],
                                    case.sizey/layersize[1],
                                    linewidth=1,
                                    facecolor=(random.random(), random.random(), random.random()),
                                    edgecolor="black"))
        plt.show()



@functools.lru_cache(maxsize=cachesize)
def SNF (cases, layersize):
    """
    *Shelf Next Fit*

    For each case, (i) determine the correct orientation, (ii) try to place it
    in the current shelf, (iii) if it does not fit open a new shelf.
     _____________________________________
    |                                     |
    |                                     |
    |_____________________________________|
    |#####|    |                          |
    |#####|####|__________________________| -> Current Shelf

    """
    X, Y = layersize
    hshelf, lastx, ceil = 0, 0, 0
    for case in cases:
        if case.sizex < case.sizey and case.sizey + lastx <= X:
            case.rotate()

        if case.sizex + lastx > X:
            lastx, hshelf = 0, ceil

        if case.sizey + hshelf > Y:
            return False

        case.x, case.y = lastx, hshelf
        lastx, ceil = case.right, max(ceil, case.top)

    return True
