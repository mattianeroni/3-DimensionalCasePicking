"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                             *  2-Dimensional Case Picking  *

In this file are implemented many 2-dimensional packing algorithms (or strip packing algorithms). They have been
written and designed to be implemented in the 2-Dimensional Case Picking algorithm that comes from the collaboration
between University of Parma, University of Modena, and Universitat Oberta de Catalunya.

For implementing all these algorithms are taken from Jukka Jylang (2010) - A Thousand Ways to Pack the Bin: A Practical
Approach to Two-Dimensional Rectangle Bin Packing.

Author: Mattia Neroni, Ph.D., Eng. (May 2021).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import functools
import random
import itertools
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt


# The cache size.
# All the results of the packing algorithms are cached to eventually speed up 
# the performance.
cachesize = 126



def test (algorithm, cases, layersize=(120,80), figsize=(10,6), **kwargs):
    """
    This method runs a specific algorithm on a given set of cases to be packed in 
    a layer, and plots the resulting solution using matplotlib library.
    
    :param algorithm: The algorithm to test.
    :param cases: The cases to pack.
    :param layersize: The size of the layer.
    :param figsize: The size of the plotted figure.
    :param **kwargs: Other eventual arguments needed by the algorithm.
    
    """
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
                * Shelf Next Fit *

    For each case:
      (i)   try to place it in the current shelf, 
      (ii)  if the ceiling of the shelf is too low, make it as high 
            as the case,
      (iii) if it does not fit open a new shelf,
      (iv)  if it still does not fit, interrupt.
    End.

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
        # If it does not fit
        if case.sizex + lastx > X:
            # Start the new shelf
            lastx, floor = 0, ceil

        if case.sizey + floor > Y:
            # If it does not fit, interrupt.
            return False
        # Place the case and eventually update the ceiling.
        case.x, case.y = lastx, floor
        lastx, ceil = case.right, max(ceil, case.top)
        
    return True



@functools.lru_cache(maxsize=cachesize)
def SFF (cases, layersize):
    """
                              * Shelf First Fit *

    For each case:
      (i)   try to place it in all the shelves starting from the bottom,
      (ii)  if it does not fit in any shelf, open a new shelf high as the case,
      (iii) if it does not fit and it is not possible to open a new shelf, interrupt.
    End.
    
    Differently from the Shelf Next Fit, even the height of the last shelf is given
    and cannot be made bigger.
                     _____________________________________
                    |_____________________________________| --> Third Shelf
                    |#########################|           |
                    |#########################|___________| --> Second Shelf
                    |#####|    |###########|              |
                    |#####|####|###########|______________| --> First Shelf

    """
    X, Y = layersize
    shelves = [[0,0,0],]  # ( lastx, floor, ceil )  For each shelf
    for case in cases:
        sizex, sizey = case.sizex, case.sizey
        
        # If we are in the first shelf the ceiling height is defined using the 
        # current case.
        if shelves[0][2] == 0:
            if sizey > Y:
                return False
            shelves[0][2] = sizey
            case.x, case.y = 0, 0
            shelves[0][0] = case.right
            continue

        for s in shelves:
            # Try to place it in the currently analysed shelf without modifying 
            # its height and without rotating the case.
            # Is there the possibility to make the ceiling higher for the last shelf?
            # For the moment this is not considered.
            lastx, floor, ceil = s
            if lastx + sizex <= X and floor + sizey <= ceil:
                case.x, case.y = lastx, floor
                s[0] = case.right
                break
        else:
            # If none of the shelves is feasible try opening a new one.
            ceil = shelves[-1][2]
            if ceil + sizey > Y:
                return False
            case.x, case.y = 0, ceil
            shelves.append([case.right, ceil, case.top])

    return True



@functools.lru_cache(maxsize=cachesize)
def SBWF (cases, layersize):
    """
                            * Shelf Best Width Fit *

    Similar to the Shelf First Fit, but the shelves are observed using a smarter logic.
    
    For each case:
      (i)   try to place the case in all the shelves going from the first one to the worst one,
      (ii)  if it does not fit in any shelf, open a new shelf high as the case,
      (iii) if it does not fit and it is not possible to open a new shelf, interrupt.
    End.
    
    In this particular case (i.e., "best width fit"), the shelves where the remaining width
    would be minimized are prioritized.

    """
    X, Y = layersize
    shelves = [[0,0,0],]  # (lastx, floor, ceil) For each shelf
    for case in cases:
        sizex, sizey = case.sizex, case.sizey

        if shelves[0][2] == 0:
            # Define the first shelf which does not exists yet.
            if sizey > Y:
                return False
            shelves[0][2] = sizey
            case.x, case.y = 0, 0
            shelves[0][0] = case.right
            continue
        # Sort feasible shelves accrding to the logic defined.
        options = sorted([s for s in shelves if sizey + s[1] <= s[2] and s[0] + sizex <= X],
                         key=lambda i: X - (i[0] + sizex),
                         reverse=False)

        if len(options) > 0:
            # If there is a feasible shelf, place the item in it.
            lastx, floor, _ = options[0]
            case.x, case.y = lastx, floor
            options[0][0] = case.right
        else:
            # If no shelf is feasible open a new shelf.
            ceil = shelves[-1][2]
            if ceil + sizey > Y:
                return False
            case.x, case.y = 0, ceil
            shelves.append([case.right, ceil, case.top])

    return True




@functools.lru_cache(maxsize=cachesize)
def SWWF (cases, layersize):
    """
                        * Shelf Worst Width Fit *

    Equal to the Shelf Best Width Fit, but the shelves where the remaining width
    is maximised are prioritized.

    """
    X, Y = layersize
    shelves = [[0,0,0],]  # (lastx, floor, ceil) For each shelf
    for case in cases:
        sizex, sizey = case.sizex, case.sizey

        if shelves[0][2] == 0:
            # Define the first shelf which does not exists yet.
            if sizey > Y:
                return False
            shelves[0][2] = sizey
            case.x, case.y = 0, 0
            shelves[0][0] = case.right
            continue
        # Sort feasible shelves accrding to the logic defined.
        options = sorted([s for s in shelves if sizey + s[1] <= s[2] and s[0] + sizex <= X],
                         key=lambda s: X - (s[0] + sizex),
                         reverse=True)
        
        if len(options) > 0:
            # If there is a feasible shelf, place the item in it.
            lastx, floor, _ = options[0]
            case.x, case.y = lastx, floor
            options[0][0] = case.right
        else:
            # If no shelf is feasible open a new shelf.
            ceil = shelves[-1][2]
            if ceil + sizey > Y:
                return False
            case.x, case.y = 0, ceil
            shelves.append([case.right, ceil, case.top])
            
    return True




@functools.lru_cache(maxsize=cachesize)
def GBAF (cases, layersize, splitting="shorteraxis"):
    """
                            * Guilliotine Best Area Fit *

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
        # Sort spaces from the smallest to the biggest one.
        F.sort(key=lambda s: s[2] * s[3])
        for i in range(len(F)):
            x, y, sizex, sizey = F[i]
            # Check the area as a preliminar control
            if sizex * sizey < case.sizex * case.sizey:
                continue
            # Try to eventually rotate the item if the are fits, but the width 
            # and the height not.
            if sizex < case.sizex or sizey < case.sizey:
                case.rotate()
                if sizex < case.sizex or sizey < case.sizey:
                    continue
            
            # If it fits place the item and remove the space from the set of spaces.
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
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])       # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longeraxis":
                    if sizex > sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])       # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "shorterleftover":
                    if sizex - case.sizex < sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])       # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longerleftover":
                    if sizex - case.sizex > sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])       # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
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
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longeraxis":
                    if sizex > sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "shorterleftover":
                    if sizex - case.sizex < sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                elif splitting == "longerleftover":
                    if sizex - case.sizex > sizey - case.sizey:
                        F.extend([(case.right, y, sizex - case.sizex, case.sizey), 
                                  (x, case.top, sizex, sizey - case.sizey)])  # Horizontal cutting
                    else:
                        F.extend([(case.right, y, sizex - case.sizex, sizey), 
                                  (x, case.top, case.sizex, sizey - case.sizey)])  # Vertical cutting
                else:
                    raise Exception("Splitting rule not defined.")

            break
        else:
            return False

    return True



def _contains (container, contained):
    x1, y1, sizex1, sizey1 = container
    x2, y2, sizex2, sizey2 = contained
    if x1 <= x2 and y1 <= y2 and x1 + sizex1 >= x2 + sizex2 and y1 + sizey1 >= y2 + sizey2:
        return True
    return False



def _equal (ispace, jspace):
    x1, y1, sizex1, sizey1 = ispace
    x2, y2, sizex2, sizey2 = jspace
    if x1 == x2 and y1 == y2 and sizex1 == sizex2 and sizey1 == sizey2:
        return True
    return False


def _split (space, overlap):
    x1, y1, sizex1, sizey1 = space
    x2, y2, sizex2, sizey2 = overlap
    newspaces = [None, None, None, None]
    if x1 < x2:
        newspaces[0] = (x1, y1, x2 - x1, sizey1)
    if (a := x1 + sizex1) > (b := x2 + sizex2):
        newspaces[1] = (b, y1, a - b, sizey1)
    if y1 < y2:
        newspaces[2] = (x1, y1, sizex1, y2 - y1)
    if (a := y1 + sizey1) > (b := y2 + sizey2):
        newspaces[3] = (x1, b, sizex1, a - b)
    return list(filter(None, newspaces))


def _overlap (case, space):
    x, y, sizex, sizey = space
    right = min(case.x + case.sizex, x + sizex)
    left = max(case.x, x)
    top = min(case.y + case.sizey, y + sizey)
    bottom = max(case.y, y)
    if top > bottom and right > left:
        return (left, bottom, right - left, top - bottom)



@functools.lru_cache(maxsize=cachesize)
def MRBL (cases, layersize):
    """
    * Maximal Rectangles Bottom Left *
    
    Similar to the guilliotine, but every time a new case is placed, no cut is made, both
    newly generated spaces are kept in memory. This introduce the necessity to make some 
    additional controls on overlaps and possible spaces containing the others.
    These aspects make this algorithm usually more performant but also slower.
    
    In this case (i.e., "bottom left") priority is given to the spaces in the bottom left
    corner.
    
    """
    X, Y = layersize
    F = [(0, 0, X, Y), ]  # (x, y, sizex, sizey) For each rectangle
    for case in cases:
        F.sort(key=lambda i: (i[0], i[1]))
        for x, y, sizex, sizey in F:
            if sizex * sizey < case.sizex * case.sizey:
                continue

            if sizex < case.sizex or sizey < case.sizey:
                case.rotate()
                if sizex < case.sizex or sizey < case.sizey:
                    continue

            case.x, case.y = x, y
            break
        else:
            return False
        
        for space in tuple(F):
            if (over := _overlap(case, space)) is not None:
                F.remove(space)
                F.extend(_split(space, over))

        to_remove = set()
        for i, j in itertools.combinations(F, 2):
            if _contains(i, j):
                to_remove.add(j)
            if _contains(j, i) and not _equal(i, j):
                to_remove.add(i)
        F = list(set(F) - to_remove)

    return True
