import functools
import random
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt


cachesize = 126


def test (algorithm, cases, layersize, figsize=(10,6)):
    suc = algorithm(cases, layersize)
    if not suc:
        print("Unsuccesful packing.")
    else:
        _, ax = plt.subplots(figsize=figsize)
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
    |.....................................| -> Ceil of shelf (not definitive)
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



@functools.lru_cache(maxsize=cachesize)
def SFF (cases, layersize):
    """
    *Shelf First Fit*

    For each case, (i) determine the correct orientation, (ii) try to place it
    in all the shelves staring from the first untils it does not fit, (iii) if
    it does not fit and it is not possible to open a new shelf returns.
     _____________________________________
    |_____________________________________| -> Third Shelf
    |#########################|           |
    |#########################|___________| -> Second Shelf
    |#####|    |###########|              |
    |#####|####|###########|______________| -> First Shelf

    """
    X, Y = layersize
    shelves = [[0,0,0],]  # (lastx, hshelf, ceil)
    for case in cases:
        if case.sizey > Y or case.sizex > X:
            return False

        for s in shelves:
            lastx, hshelf, ceil = s
            if sizey < sizex and (sizex + hshelf <= ceil or ceil == 0):
                case.rotate()

            sizex, sizey = case.sizex, case.sizey
            if ceil == 0:
                ceil = sizey
                s[2] = sizey

            if lastx + sizex <= X and hshelf + sizey <= ceil:
                case.x, case.y = lastx, hshelf
                s[0] = case.right
                break
            # Possibility to make the ceiling higher for the last shelf?
        else:
            ceil = shelves[-1][2]
            if ceil + sizey > Y:
                return False

            shelves.append([0, ceil, ceil+sizey])
            case.x, case.y = 0, ceil

    return True



@functools.lru_cache(maxsize=cachesize)
def SBWF (cases, layersize):
    """
    *Shelf Best Width Fit*

    Similar to the First Fit, but the shelves are tried using a smarter logic.

    For each case, (i) determine the correct orientation, (ii) try to place it
    in all the shelves prioritizing those in which the maining width is
    minimized, (iii) if it does not fit and it is not possible to open a new
    shelf returns.

    """
    X, Y = layersize
    shelves = [[0,0,0],]  # (lastx, hshelf, ceil)
    pass
