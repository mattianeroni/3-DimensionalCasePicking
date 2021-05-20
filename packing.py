import functools
import random
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt


cachesize = 126


def test (algorithm, cases, layersize, figsize=(10,6), **kwargs):
    suc = algorithm(cases, layersize, **kwargs)
    if not suc:
        print("Unsuccesful packing.")
    else:
        _, ax = plt.subplots(figsize=figsize)
        ax.add_patch(Rectangle((0,0), 1, 1, linewidth=3, edgecolor='r', facecolor='none'))
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
    floor, lastx, ceil = 0, 0, 0
    for case in cases:
        if case.sizex + lastx > X:
            lastx, floor = 0, ceil

        if case.sizey + floor > Y:
            return False

        case.x, case.y = lastx, floor
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
    shelves = [[0,0,0],]  # (lastx, floor, ceil) for each shelf
    for case in cases:
        sizex, sizey = case.sizex, case.sizey

        if shelves[0][2] == 0:
            shelves[0][2] = sizey
            case.x, case.y = 0, 0
            shelves[0][0] = case.right
            continue

        for s in shelves:
            lastx, floor, ceil = s

            if lastx + sizex <= X and floor + sizey <= ceil:
                case.x, case.y = lastx, floor
                s[0] = case.right
                break
            # Is there the possibility to make the ceiling higher for the last shelf?
            # For the moment this is not considered.
        else:
            ceil = shelves[-1][2]
            if ceil + sizey > Y:
                return False

            case.x, case.y = 0, ceil
            shelves.append([case.right, ceil, case.top])

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
    shelves = [[0,0,0],]  # (lastx, floor, ceil) for each shelf
    for case in cases:
        sizex, sizey = case.sizex, case.sizey

        if shelves[0][2] == 0:
            shelves[0][2] = sizey
            case.x, case.y = 0, 0
            shelves[0][0] = case.right
            continue

        options = sorted([s for s in shelves if sizey + s[1] <= s[2] and s[0] + sizex <= X],
                         key=lambda i: X - (i[0] + sizex),
                         reverse=False)

        if len(options) > 0:
            lastx, floor, _ = options[0]
            case.x, case.y = lastx, floor
            options[0][0] = case.right
        else:
            ceil = shelves[-1][2]
            if ceil + sizey > Y:
                return False

            case.x, case.y = 0, ceil
            shelves.append([case.right, ceil, case.top])

    return True




@functools.lru_cache(maxsize=cachesize)
def SWWF (cases, layersize):
    """
    *Shelf Worst Width Fit*

    Equal to the Shelf Best Width Fit, but the shelves where the remaining width
    is maximised are prioritized.

    """
    X, Y = layersize
    shelves = [[0,0,0],]  # (lastx, floor, ceil) for each shelf
    for case in cases:
        sizex, sizey = case.sizex, case.sizey

        if shelves[0][2] == 0:
            shelves[0][2] = sizey
            case.x, case.y = 0, 0
            shelves[0][0] = case.right
            continue

        options = sorted([s for s in shelves if sizey + s[1] <= s[2] and s[0] + sizex <= X],
                         key=lambda s: X - (s[0] + sizex),
                         reverse=True)
        if len(options) > 0:
            lastx, floor, _ = options[0]
            case.x, case.y = lastx, floor
            options[0][0] = case.right
        else:
            ceil = shelves[-1][2]
            if ceil + sizey > Y:
                return False

            case.x, case.y = 0, ceil
            shelves.append([case.right, ceil, case.top])
    return True




@functools.lru_cache(maxsize=cachesize)
def GBAF (cases, layersize, splitting="shorteraxis"):
    """
    *Guilliotine Best Area Fit*

    This algorithm keeps track of all the empty spaces still available. Every time
    a new case is placed in one of these spaces, it is replaced with two new spaces
    breaking down the L-shaped space into two smaller rectangles.

       Vertical Cutting            Horizontal Cutting
     ____________________         ____________________
    |    |               |       |                    |
    |____|               |       |____________________|
    |####|               |       |####|               |
    |####|_______________|       |####|_______________|


    In this particular case of "best area fit", priority is given to the
    spaces characterised by smallest area.

    """
    X, Y = layersize
    F = [(0, 0, X, Y), ]  # (x, y, sizex, sizey) For each rectangle

    for case in cases:
        F.sort(key=lambda s: s[2] * s[3])
        for i in range(len(F)):
            space = F[i]
            x, y, sizex, sizey = space
            if sizex < case.sizex or sizey < case.sizey:
                case.rotate()
                if sizex < case.sizex or sizey < case.sizey:
                    continue

            case.x, case.y = x, y
            F.pop(i)

            if (sizex, sizey) == (case.sizex, case.sizey):
                pass
            elif sizey == case.sizey:
                F.append((case.right, y, sizex - case.sizex, sizey))
            elif sizex == case.sizex:
                F.append((x, case.top, sizex, sizey - case.sizey))
            else:
                if splitting == "shorteraxis":
                    if sizex < sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longeraxis":
                    if sizex > sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "shorterleftover":
                    if sizex - case.sizex < sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longerleftover":
                    if sizex - case.sizex > sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                else:
                    raise Exception("Splitting rule not defined.")

            break
        else:
            return False

    return True



@functools.lru_cache(maxsize=cachesize)
def GWAF (cases, layersize, splitting="shorteraxis"):
    """
    *Guilliotine Worst Area Fit*

    Very similar to the Guilliotine Best Area Fit, however, in this case, is
    given priority to the bigger spaces. Most of the times it should provide a
    worst solution, but there are some lucky situations and this approach is
    computationally faster.

    """
    X, Y = layersize
    F = [(0, 0, X, Y), ]  # (x, y, sizex, sizey) For each rectangle

    for case in cases:
        F.sort(key=lambda s: s[2] * s[3], reverse=True)
        for i in range(len(F)):
            space = F[i]
            x, y, sizex, sizey = space

            if sizex * sizey < case.sizex * case.sizey:
                return False
                
            if sizex < case.sizex or sizey < case.sizey:
                case.rotate()
                if sizex < case.sizex or sizey < case.sizey:
                    continue

            case.x, case.y = x, y
            F.pop(i)

            if (sizex, sizey) == (case.sizex, case.sizey):
                pass
            elif sizey == case.sizey:
                F.append((case.right, y, sizex - case.sizex, sizey))
            elif sizex == case.sizex:
                F.append((x, case.top, sizex, sizey - case.sizey))
            else:
                if splitting == "shorteraxis":
                    if sizex < sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longeraxis":
                    if sizex > sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "shorterleftover":
                    if sizex - case.sizex < sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longerleftover":
                    if sizex - case.sizex > sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                else:
                    raise Exception("Splitting rule not defined.")

            break
        else:
            return False

    return True
