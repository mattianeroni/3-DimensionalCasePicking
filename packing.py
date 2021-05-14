import functools


cachesize = 126


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
            return False, cases

        case.x, case.y = lastx, hshelf
        lastx, ceil = case.right, max(ceil, case.top)

    return True, cases
